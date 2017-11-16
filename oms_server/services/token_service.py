import time
import logging
from datetime import datetime
from oms.models.store import Store
from oms_server.services.platforms import interface
from oms_server.services.platforms import common_params


class TokenService:

    # 定时任务定时刷新token
    @staticmethod
    def refresh():
        stores = Store.objects.all()
        for store in stores:
            TokenService().refresh_store_token(store)

    # 返回是否成功
    @staticmethod
    def refresh_store_token(store):
        store_detail = {
            "app_key": store.app_key,
            "app_secret": store.app_secret,
            "expire_in": store.expire_in,
            "access_token": store.access_token,
            "access_token_expire_time": store.access_token_expire_time,
            "refresh_token_expire_time": store.refresh_token_expire_time,
            "refresh_token": store.refresh_token,
            "store_key": store.store_key,
            "platform_name": store.platform_name,
            "store_name": store.store_name,
        }

        access_token, error_msg = interface.refresh_token(
            store.platform_name, store_detail)
        if isinstance(error_msg, str) and len(error_msg):
            logging.info("%s[%s]refresh_token失败，error:%s" % (store.store_name, store.platform.name, error_msg))
        if access_token:
            store.access_token = store_detail['access_token']
            store.expire_in = store_detail['expire_in']
            store.refresh_token = store_detail["refresh_token"]
            expire_time = datetime.now().timestamp() + store.expire_in
            store.access_token_expire_time = datetime.fromtimestamp(
                expire_time)
            store.refresh_token_expire_time = store.refresh_token_expire_time
            store.save()
            logging.info("%s[%s]refresh_token成功" % (store.store_name, store.platform.name))
            return True
        else:
            return False
