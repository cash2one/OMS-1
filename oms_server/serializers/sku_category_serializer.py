# -*- coding: UTF-8 -*-
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from oms.models.sku_category import SkuCategory
from oms_server.serializers.extension import TimestampField
from oms_server.serializers.extension import UUIDField


class SuperCategoryField(serializers.RelatedField):

    def to_representation(self, value):
        print(".....")
        print(value)
        if not value:
            return '主类目'
        else:
            print("Hello")
            return value.category_name


class SubCategorySerializer(serializers.ModelSerializer):

    # id = UUIDField(required=False)
    created_at = TimestampField(required=False)
    updated_at = TimestampField(required=False)

    class Meta:
        model = SkuCategory
        fields = [
            'id', 'created_at', 'updated_at',
            'category_name'
        ]


class SkuCategorySerializer(ModelSerializer):

    # id = UUIDField(required=False)
    created_at = TimestampField(required=False)
    updated_at = TimestampField(required=False)
    sub_category = SubCategorySerializer(many=True)

    class Meta:
        model = SkuCategory
        fields = [
            'id', 'created_at', 'updated_at', 'sub_category',
            'category_name'
        ]
