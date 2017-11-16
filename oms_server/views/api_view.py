from rest_framework import status
from rest_framework.decorators import api_view
from oms.extension.response_wrapper import JsonResponse


BASE_URL = '127.0.0.1'
LASTEST_VERSION = 'v1'


def cache_control(func):
    def wrapper(request, *args, **kwargs):
        api_version = request.META.get('HTTP_API_VERSION')
        print(api_version)
        if api_version == LASTEST_VERSION:
            return JsonResponse(data={},
                                headers={'api-version': LASTEST_VERSION},
                                status=status.HTTP_304_NOT_MODIFIED)
        else:
            return func(request, *args, **kwargs)
    return wrapper


API = {
    'stock_in': {
        'url': 'stock_in',
        'STOCK_IN_STATUS': {
            'NEW': '未开始处理',
            'ACCEPT': '仓库接单',
            'PARTFULFILLED': '部分收货完成',
            'FULFILLED': '收货完成',
            'EXCEPTION': '异常',
            'CANCELED': '取消',
            'CLOSED': '关闭',
            'REJECT': '拒单',
            'CANCELEDFAIL': '取消失败'
        },
        'STOCK_IN_TYPE': {
            1: '正常入库单',
            2: '退货入库单'
        }
    },
    'balance': {
        'url': 'balance',
        'STATEMENT_TYPE': {
            1: '充值',
            2: '发货收入',
            3: '仓储收入',
            11: '账单支出',
            12: '面单支出',
            13: '提现'
        }
    },
    'bill': {
        'url': 'bill',
        'BILL_TYPE': {
            1: '发货账单',
            2: '仓储账单'
        }
    },
    'receipt': {
        'url': 'receipt',
        'RECEIPT_TYPE': {
            1: '发货收入',
            2: '仓储收入'
        }
    },
    'deposit': {
        'url': 'deposit',
        'DEPOSIT_TYPE': {
            1: '充值',
            2: '提现'
        }
    }
}


@api_view(['GET'])
@cache_control
def api(request):
    return JsonResponse(data=API, headers={'api-version': LASTEST_VERSION})
