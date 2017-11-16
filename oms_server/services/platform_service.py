# -*- coding: UTF-8 -*-
from oms.models.plat import Plat
from oms.extension.exception import CustomException


class PlatformService:

    def create(self, data):
        # 检查平台是否存在
        plat = Plat.objects.filter(name=data['platform_name'])
        if plat:
            raise CustomException(10004)
        plat = Plat(
            name=data['platform_name'],
            interface=data.get('interface'),
            callback=data.get('callback'),
            need_store_key=data.get('need_store_key', False),
            is_jointed=data.get('is_jointed', False)
        )
        plat.save()
        # Plat.objects.bulk_create([plat], set_primary_keys=True)
        # print("=================================")
        # print(plat.id)
        # print("==============================")
        return plat

    def list(self):
        platforms = Plat.objects.filter(is_deleted=False)
        return platforms

    def get(self, platform_id):
        pass

    def update(self, paltform_id, data):
        pass
