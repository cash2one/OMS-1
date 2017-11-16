from django.core.exceptions import ObjectDoesNotExist
from oms.extension.error_code import ERROR_MSG
from oms.models.sku import Sku
from oms.models.plat import Plat
from oms.models.order import Order
from oms.models.store import Store
from oms.models.stock_in import StockIn
from oms.models.activity_sku import ActivitySku
from oms.models.order_detail import OrderDetail
from oms.models.sku_category import SkuCategory
from oms.models.sku_warehouse import SkuWarehouse
from oms.models.activity_rule import ActivityRule
from oms.models.stock_transfer import StockTransfer
from oms.models.stock_in_detail import StockInDetail

"""
关于 使用异常还是错误码的权衡与选择：
    异常：在正常程序控制流之外，或者是程序异常
    https://www.zhihu.com/question/36278363
    https://segmentfault.com/q/1010000004166896
"""


class CustomException(Exception):

    def __init__(self, error_code, error_message=None):
        self.error_code = error_code
        if error_message is None:
            self.error_message = ERROR_MSG.get(
                error_code, 'There were some strange mistakes!')
        else:
            self.error_message = error_message


class CopException(Exception):

    def __init__(self, method, extra_message=None):
        if method == 'singleitem.synchronize':
            self.error_code = 40001
            self.error_message = '同步商品失败:' + extra_message
        elif method == 'entryorder.create':
            self.error_code = 40002
            self.error_message = '同步入库单失败:' + extra_message


class PingppException(Exception):

    pass


class NotExistException(ObjectDoesNotExist):

    def __init__(self, exc):
        self.error_code = 10000
        self.error_message = 'There were some strange mistakes!'
        if isinstance(exc, Sku.DoesNotExist):
            self.error_code = 10001
            self.error_message =\
                ERROR_MSG.get(10001, '商品不存在')
        elif isinstance(exc, SkuCategory.DoesNotExist):
            self.error_code = 10002
            self.error_message =\
                ERROR_MSG.get(10002, '商品分类不存在')
        elif isinstance(exc, SkuWarehouse.DoesNotExist):
            self.error_code = 10003
            self.error_message =\
                ERROR_MSG.get(10003, '库存不存在')
        elif isinstance(exc, Order.DoesNotExist):
            self.error_code = 10004
            self.error_message =\
                ERROR_MSG.get(10004, '订单不存在')
        elif isinstance(exc, OrderDetail.DoesNotExist):
            self.error_code = 10005
            self.error_message =\
                ERROR_MSG.get(10005, '订单详情不存在')
        elif isinstance(exc, ActivityRule.DoesNotExist):
            self.error_code = 10006
            self.error_message =\
                ERROR_MSG.get(10006, '活动不存在')
        elif isinstance(exc, ActivitySku.DoesNotExist):
            self.error_code = 10007
            self.error_message =\
                ERROR_MSG.get(10007, '活动商品不存在')
        elif isinstance(exc, Plat.DoesNotExist):
            self.error_code = 10008
            self.error_message =\
                ERROR_MSG.get(10008, '平台不存在')
        elif isinstance(exc, StockIn.DoesNotExist):
            self.error_code = 10009
            self.error_message =\
                ERROR_MSG.get(10009, '入库单不存在')
        elif isinstance(exc, StockInDetail.DoesNotExist):
            self.error_code = 10010
            self.error_message =\
                ERROR_MSG.get(10010, '入库单详情不存在')
        elif isinstance(exc, StockTransfer.DoesNotExist):
            self.error_code = 10011
            self.error_message =\
                ERROR_MSG.get(10011, '库存调拨单不存在')
        elif isinstance(exc, Store.DoesNotExist):
            self.error_code = 10012
            self.error_message =\
                ERROR_MSG.get(10012, '店铺不存在')
