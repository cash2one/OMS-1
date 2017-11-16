# -*- coding: UTF-8 -*-
import datetime
from django.db import transaction
from oms.models.sku import Sku
from oms.models.store import Store
from oms.models.activity_sku import ActivitySku
from oms.models.activity_rule import ActivityRule
from oms.extension.exception import CustomException


class ActivityService:

    @classmethod
    @transaction.atomic
    def create(cls, store_id, data):
        try:
            store = Store.objects.get(id=store_id)
            activity_rule = ActivityRule(
                rule_type=data['rule_type'],
                title=data['title'],
                begin_date=data['begin_date'],
                end_date=data['end_date'],
                accord_cost=data.get('accord_cost', 0),
                is_times=data.get('is_times', False),
                accord_amount=data.get('accord_amount', 0),
                store=store
            )
            activity_rule.save()
            print(activity_rule.id)
            for sku_info in data['skus']:
                sku = Sku.objects.get(id=sku_info['sku_id'])
                activity_sku = ActivitySku(
                    sku=sku,
                    is_gift=sku_info.get('is_gift', False),
                    count=sku_info.get('count', 1),
                    activity_rule=activity_rule)
                activity_sku =\
                    ActivitySku(sku=sku,
                                is_gift=sku_info.get('is_gift', False),
                                count=sku_info.get('count', 1),
                                activity_rule=activity_rule)
                activity_sku.save()
            return {'success': True}
        except Exception as e:
            print(e)
            return {'success': False, 'error_code': '10003'}
        store = Store.objects.get(id=store_id)
        activity_rule = ActivityRule(
            rule_type=data['rule_type'],
            title=data['title'],
            begin_date=data['begin_date'],
            end_date=data['end_date'],
            accord_cost=data.get('accord_cost', 0),
            is_times=data.get('is_times', False),
            accord_amount=data.get('accord_amount', 0),
            store=store
        )
        activity_rule.save()
        for sku_info in data['skus']:
            sku = Sku.objects.get(id=sku_info['sku_id'])
            activity_sku =\
                ActivitySku(sku=sku,
                            is_gift=sku_info.get('is_gift', False),
                            count=sku_info.get('count', 1),
                            activity_rule=activity_rule)
            activity_sku.save()
        return None

    @classmethod
    def get(cls, store_id):
        rules = ActivityRule.objects.filter(
            store__id=store_id,
            is_enabled=True)
        all_rules = []
        for rule in rules:
            sku_gifts, skus = cls.rule_get_sku(rule=rule)
            rule_result = {
                'activity_id': rule.id,
                'activity_type': rule.rule_type,
                'begin_time': datetime.datetime.strftime(
                    rule.begin_date, '%Y-%m-%d %H:%M:%S'),
                'end_time': datetime.datetime.strftime(
                    rule.end_date, '%Y-%m-%d %H:%M:%S'),
                'gift_sku': sku_gifts
            }
            if rule.rule_type == 1:
                rule_result['accord_cost'] = rule.accord_cost
                rule_result['is_times'] = rule.is_times
            elif rule.rule_type == 2:
                rule_result['accord_count'] = rule.accord_amount
                rule_result['sku'] = skus
            all_rules.append(rule_result)

        return all_rules

    @classmethod
    def rule_get_sku(cls, rule):
        activity_skus = ActivitySku.objects.filter(activity_rule=rule, is_deleted=False)
        sku_gifts = []
        skus = []
        for activity_sku in activity_skus:
            if activity_sku.is_gift:
                sku_gifts.append({'sku_id': activity_sku.sku.id, 'item_code': activity_sku.sku.item_code, 'count': activity_sku.count})
            else:
                skus.append({'sku_id': activity_sku.sku.id})
        return sku_gifts, skus
