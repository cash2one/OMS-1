# -*- coding: UTF-8 -*-
from django.db.models import Prefetch
from oms.models.sku_category import SkuCategory


class SkuCategoryService:

    def create(self, user_id, data):
        sku_category = SkuCategory(
            category_name=data['category_name'],
            user_id=user_id
        )
        if 'super_category_id' in data.keys():
            super_category = SkuCategory.objects.\
                get(id=data['super_category_id'],
                    user_id=user_id)
            sku_category.super_category_id = super_category.id
        sku_category.save()
        return sku_category

    def list(self, user_id):
        sub_category = SkuCategory.objects.\
            filter(is_deleted=False)
        sku_categories = SkuCategory.objects.\
            prefetch_related(
                 Prefetch('sub_category', queryset=sub_category)
            ).\
            filter(user_id=user_id,
                   super_category=None,
                   is_deleted=False)
        return sku_categories

    def get(self, sku_category_id, user_id):
        sku_category = SkuCategory.objects.\
            get(id=sku_category_id,
                is_deleted=False,
                user_id=user_id)
        return sku_category

    def update(self, sku_category_id, user_id, data):
        sku_category = SkuCategory.objects.\
            get(id=sku_category_id,
                user_id=user_id,
                is_deleted=False)
        update_fileds = ['category_name',
                         'super_category_id']
        for key in data.keys():
            if key in update_fileds:
                setattr(sku_category, key, data[key])
        sku_category.save()
        return sku_category

    def delete(self, sku_category_id, user_id):
        sku_category = SkuCategory.objects.\
            get(id=sku_category_id)
        sku_category.is_deleted = True
        # 关联删除
        if not sku_category.super_category_id:
            SkuCategory.objects.\
                filter(super_category_id=sku_category.id,
                       is_deleted=False).\
                update(is_deleted=True)
        sku_category.save()
        return sku_category
