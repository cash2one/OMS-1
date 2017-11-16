# -*- coding: UTF-8 -*-
from django.db.models import Prefetch
from django.core.paginator import Paginator
from django.db import transaction
from oms.models.sku import Sku
from oms.models.activity_sku import ActivitySku
from oms.models.activity_rule import ActivityRule
from oms.models.store import Store
from oms.extension.exception import CustomException


class ActivityService:

    # 事务一致性
    @transaction.atomic
    def create(self, user_id, store_ids, data):
        try:
            stores = Store.objects.\
                filter(id__in=store_ids,
                       user_id=user_id)
            # 活动检查
            self.check(data, store_ids)
            activities = []
            activity_skues = []
            print(stores)
            for store in stores:
                # 满元赠
                if int(data.get('rule_type', 0)) == 1:
                    # 活动规则创建
                    activity_rule = ActivityRule(
                        title=data['title'],
                        rule_type=int(data['rule_type']),
                        begin_date=data['begin_date'],
                        end_date=data['end_date'],
                        accord_cost=data.get('accord_cost', 0),
                        is_times=data.get('is_times', False),
                        store=store,
                        user_id=user_id
                    )
                    activity_rule.save()
                    activity_rule.gifts = []
                    # 赠品添加
                    for gift_data in data['gifts']:
                        if gift_data.get('sku_id', ''):
                            gift = Sku.objects.get(id=gift_data['sku_id'])
                            activity_gift = ActivitySku(
                                is_gift=True,
                                count=gift_data['count'],
                                sku=gift,
                                activity_rule=activity_rule
                            )
                            activity_skues.append(activity_gift)
                            activity_rule.gifts.append(activity_gift)
                    activities.append(activity_rule)
                elif int(data.get('rule_type', 0)) == 2:
                    # 满件赠
                    activity_rule = ActivityRule(
                        title=data['title'],
                        rule_type=int(data['rule_type']),
                        begin_date=data['begin_date'],
                        end_date=data['end_date'],
                        accord_amount=data.get('accord_amount', 0),
                        store=store,
                        user_id=user_id
                    )
                    activity_rule.save()
                    activities.append(activity_rule)
                    activity_rule.skues = []
                    for sku_data in data['skues']:
                        if sku_data.get('sku_id', ''):
                            sku = Sku.objects.get(id=sku_data['sku_id'])
                            activity_sku = ActivitySku(
                                is_gift=False,
                                sku=sku,
                                activity_rule=activity_rule
                            )
                            activity_skues.append(activity_sku)
                            activity_rule.skues.append(activity_sku)
                    activity_rule.gifts = []
                    # 赠品添加
                    for gift_data in data['gifts']:
                        if gift_data.get('sku_id', ''):
                            gift = Sku.objects.get(id=gift_data['sku_id'])
                            activity_gift = ActivitySku(
                                is_gift=True,
                                count=gift_data['count'],
                                sku=gift,
                                activity_rule=activity_rule
                            )
                            activity_skues.append(activity_gift)
                            activity_rule.gifts.append(activity_gift)
            # 批量创建 
            # bulk_create 不支持mysql生成id(pstgresql)
            # ActivityRule.objects.bulk_create(activities)
            for _ in activities:
                print(_.id)
                print("---------------")
            ActivitySku.objects.bulk_create(activity_skues)
            return activities
        except Exception as e:
            print("==================")
            print(e)
            raise CustomException(10010)

    def list(self, user_id, page, page_size):
        activity_rules = ActivityRule.objects.\
            select_related('store').\
            filter(is_deleted=False,
                   user_id=user_id)
        paginator = Paginator(activity_rules, page_size)
        return paginator

    def get(self, activity_rule_id, user_id):
        gifts = ActivitySku.objects.\
            select_related('sku').\
            filter(is_gift=True,
                   is_deleted=False)
        skues = ActivitySku.objects.\
            select_related('sku').\
            filter(is_gift=False,
                   is_deleted=False)
        activity_rule = ActivityRule.objects.\
            select_related('store').\
            prefetch_related(
                Prefetch('activitysku_set', queryset=gifts, to_attr='gifts')
            ).\
            prefetch_related(
                Prefetch('activitysku_set', queryset=skues, to_attr='skues')
            ).\
            filter(is_deleted=False, user_id=user_id).\
            get(id=activity_rule_id)
        return activity_rule

    # 活动检查：
    # 时间格式检查
    # 满元活动店铺唯一检查
    def check(self, data, store_ids):
        # 满元赠
        if data.get('rule_type') == 1:
            exist = ActivityRule.objects.\
                filter(rule_type=1, is_deleted=False,
                       is_expired=False, store_id__in=store_ids)
            if exist:
                raise CustomException("店铺下已存在正在进行的满元赠活动")

    # 必然是全部更新
    # 事务一致性
    @transaction.atomic
    def update(self, activity_rule_id, user_id, data):
        activity_rule = self.update_activity_rule(user_id, activity_rule_id, data)
        create_activity_skues = []
        # 满元赠活动
        if int(data['rule_type']) == 1:
            if data.get('gifts'):
                self.edit_gift(activity_rule=activity_rule,
                               data=data,
                               create_activity_skues=create_activity_skues)
        elif int(data['rule_type']) == 2:
            if data.get('gifts'):
                self.edit_gift(activity_rule=activity_rule,
                               data=data,
                               create_activity_skues=create_activity_skues)
            if data.get('skues'):
                self.edit_sku(activity_rule=activity_rule,
                              data=data,
                              create_activity_skues=create_activity_skues)
        # 批量创建和批量删除
        ActivitySku.objects.bulk_create(create_activity_skues)
        # ActivitySku.objects.\
        #     filter(id__in=delete_activity_sku_ids).\
        #     update(is_deleted=True)
        activity_rule = self.get(activity_rule_id=activity_rule.id,
                                 user_id=user_id)
        return activity_rule

    def toggle_enable_activity(self, activity_rule_id, user_id):
        ''' 开启/关闭活动 '''
        activity_rule = ActivityRule.objects.\
            get(id=activity_rule_id, user_id=user_id, is_deleted=False)
        activity_rule.is_enabled = not activity_rule.is_enabled
        activity_rule.save()
        return activity_rule

    # 更新活动属性
    def update_activity_rule(self, user_id, activity_rule_id, data):
        activity_rule = ActivityRule.objects.\
            get(id=activity_rule_id, user_id=user_id)
        update_fileds = ['title', 'is_enabled', 'begin_date', 'end_date',
                         'rule_type', 'accord_cost', 'accord_amount',
                         'store_id', 'is_times']
        for i in data.keys():
            if i in update_fileds:
                setattr(activity_rule, i, data[i])
        # 不分情况，更新的时候批量删除之前关联的ActivitySku
        ActivitySku.objects.\
            filter(activity_rule_id=activity_rule.id).\
            filter(is_deleted=False).\
            update(is_deleted=True)
        # 根据营销类型，选择accord_cost/accord_amount
        if int(data['rule_type']) == 1:
            activity_rule.accord_cost = data.get('accord_cost')
            activity_rule.accord_amount = None
        elif int(data['rule_type']) == 2:
            activity_rule.accord_amount = data.get('accord_amount')
            activity_rule.accord_cost = None
        activity_rule.save()
        return activity_rule

    # 更新活动赠品
    def update_activity_gift(self, activity_gift_id, data):
        activity_gift = ActivitySku.objects.get(id=activity_gift_id)
        # 更新数量
        activity_gift.count = data['count']

    def edit_gift(self, activity_rule, data,
                  create_activity_skues):
        for gift_data in data['gifts']:
            gift = Sku.objects.get(id=gift_data['sku_id'])
            activity_gift = ActivitySku(
                is_gift=True,
                count=gift_data['count'],
                sku=gift,
                activity_rule=activity_rule
            )
            create_activity_skues.append(activity_gift)

    def edit_sku(self, activity_rule, data,
                 create_activity_skues):
        for sku_data in data['skues']:
            sku = Sku.objects.get(id=sku_data['sku_id'])
            activity_sku = ActivitySku(
                is_gift=False,
                sku=sku,
                activity_rule=activity_rule
            )
            create_activity_skues.append(activity_sku)

    def delete(self, activity_rule_id, user_id):
        activity_rule = ActivityRule.objects.\
            get(user_id=user_id, id=activity_rule_id)
        if activity_rule.is_enabled:
            raise CustomException('10012', "活动开启状态无法删除")
        else:
            activity_rule.is_deleted = True
            activity_rule.save()
            ActivitySku.objects.\
                filter(activity_rule_id=activity_rule.id).\
                filter(is_deleted=False).\
                update(is_deleted=True)
        return activity_rule
