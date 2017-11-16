# -*- coding: UTF-8 -*-
from django.utils import timezone
from django.db.models import Sum
from dateutil.relativedelta import relativedelta
from oms.models.order_bill import OrderBill
from oms.models.order_receipt import OrderReceipt
from oms.models.storge_receipt import StorgeReceipt
from oms.models.storge_bill import StorgeBill
from oms.models.order import Order
from oms.models.sku_warehouse import SkuWarehouse
from oms_server.http_service.warehouse_service \
    import get_used_warehouse_operation_info, get_shared_warehouse_operation_info


class OperationService(object):

    # {
    #     "total_income": "1000056",
    #     "total_orders": "32511",
    #     "current_month_income": "12345",
    #     "current_month_orders": "12345",
    #     "runtime": "123",
    #     "share_acreage": "5000",
    #     "total_inventory": "12300",
    #     "users": "105",
    #     "month_income_list": [
    #         {
    #             "month": "9",
    #             "income": "12345"
    #         },
    #         {
    #             "month": "8",
    #             "income": "12345"
    #         },
    #         {
    #             "month": "7",
    #             "income": "12345"
    #         }
    #     ],
    #     "month_orders_list": [
    #         {
    #             "month": "9",
    #             "orders": "12345"
    #         },
    #         {
    #             "month": "8",
    #             "orders": "12345"
    #         },
    #         {
    #             "month": "7",
    #             "orders": "12345"
    #         }
    #     ],
    #     "month_users_list": [
    #         {
    #             "month": "9",
    #             "users": "12345"
    #         },
    #         {
    #             "month": "8",
    #             "users": "12345"
    #         },
    #         {
    #             "month": "7",
    #             "users": "12345"
    #         }
    #     ]
    # }
    @classmethod
    def shared_warehouse_info(cls, user_id, warehouse_id, token):
        data = {}
        amount = \
            OrderReceipt.objects.filter(
                warehouse_id=warehouse_id).aggregate(Sum('amount'))
        order_receipt = amount['amount__sum'] or 0
        amount = \
            StorgeReceipt.objects.filter(
                warehouse_id=warehouse_id).aggregate(Sum('amount'))
        storge_receipt = amount['amount__sum'] or 0
        data['total_income'] = storge_receipt + order_receipt

        quantity = \
            SkuWarehouse.objects.filter(
                warehouse_id=warehouse_id).aggregate(Sum('quantity'))
        data['total_inventory'] = quantity['quantity__sum'] or 0

        data['total_orders'] = \
            Order.objects.filter(warehouse_id=warehouse_id).count()

        current_month = timezone.now().month
        current_year = timezone.now().year
        data['current_month_orders'] = \
            Order.objects.filter(
                warehouse_id=warehouse_id,
                created_at__month=current_month,
                created_at__year=current_year).count()

        amount = \
            OrderReceipt.objects.filter(
                warehouse_id=warehouse_id,
                created_at__month=current_month,
                created_at__year=current_year).aggregate(Sum('amount'))
        order_receipt = amount['amount__sum'] or 0
        amount = \
            StorgeReceipt.objects.filter(
                warehouse_id=warehouse_id,
                created_at__month=current_month,
                created_at__year=current_year).aggregate(Sum('amount'))
        storge_receipt = amount['amount__sum'] or 0

        data['current_month_income'] = storge_receipt + order_receipt

        data['month_income_list'] = []
        data['month_income_list'].append(
            {'month': str(current_month), 'income': data['current_month_income']})

        data['month_orders_list'] = []
        data['month_orders_list'].append(
            {'month': str(current_month), 'orders': data['current_month_orders']})

        for num in [1, 2]:
            time = timezone.now() + relativedelta(months=-num)
            month = time.month
            year = time.year
            orders = \
                Order.objects.filter(
                    warehouse_id=warehouse_id,
                    created_at__month=month,
                    created_at__year=year).count()

            amount = \
                OrderReceipt.objects.filter(
                    warehouse_id=warehouse_id,
                    created_at__month=month,
                    created_at__year=year).aggregate(Sum('amount'))
            order_receipt = amount['amount__sum'] or 0
            amount = \
                StorgeReceipt.objects.filter(
                    warehouse_id=warehouse_id,
                    created_at__month=month,
                    created_at__year=year).aggregate(Sum('amount'))
            storge_receipt = amount['amount__sum'] or 0

            income = storge_receipt + order_receipt

            data['month_orders_list'].append(
                {'month': str(month), 'orders': orders})
            data['month_income_list'].append(
                {'month': str(month), 'income': income})

        result = get_shared_warehouse_operation_info(warehouse_id, token)
        if result:
            data['runtime'] = result['runtime']
            data['users'] = result['users']
            data['share_acreage'] = result['share_acreage']
            data['month_users_list'] = result['month_users_list']
        return data

    # {
    #     "total_bill": "1000056",
    #     "total_orders": "32511",
    #     "current_month_bill": "12345",
    #     "current_month_orders": "12345",
    #     "used_time": "123",
    #     "total_inventory": "12300",
    #     "month_bill_list": [
    #         {
    #             "month": "9",
    #             "bill": "12345"
    #         },
    #         {
    #             "month": "8",
    #             "bill": "12345"
    #         },
    #         {
    #             "month": "7",
    #             "bill": "12345"
    #         }
    #     ],
    #     "month_orders_list": [
    #         {
    #             "month": "9",
    #             "orders": "12345"
    #         },
    #         {
    #             "month": "8",
    #             "orders": "12345"
    #         },
    #         {
    #             "month": "7",
    #             "orders": "12345"
    #         }
    #     ],
    # }
    @classmethod
    def used_warehouse_info(cls, user_id, warehouse_id, token):
        data = {}
        amount = \
            OrderBill.objects.filter(
                warehouse_id=warehouse_id,
                user_id=user_id).aggregate(Sum('amount'))
        order_bill = amount['amount__sum'] or 0
        amount = \
            StorgeBill.objects.filter(
                warehouse_id=warehouse_id,
                user_id=user_id).aggregate(Sum('amount'))
        storge_bill = amount['amount__sum'] or 0

        data['total_bill'] = order_bill + storge_bill

        data['total_orders'] = \
            Order.objects.filter(
                warehouse_id=warehouse_id,
                user_id=user_id).count()

        quantity = \
            SkuWarehouse.objects.filter(
                warehouse_id=warehouse_id,
                user_id=user_id).aggregate(Sum('quantity'))
        data['total_inventory'] = quantity['quantity__sum'] or 0

        current_month = timezone.now().month
        current_year = timezone.now().year
        data['current_month_orders'] = \
            Order.objects.filter(
                warehouse_id=warehouse_id,
                user_id=user_id,
                created_at__month=current_month,
                created_at__year=current_year).count()

        amount = \
            OrderBill.objects.filter(
                warehouse_id=warehouse_id,
                user_id=user_id,
                created_at__month=current_month,
                created_at__year=current_year).aggregate(Sum('amount'))
        order_bill = amount['amount__sum'] or 0
        amount = \
            StorgeBill.objects.filter(
                warehouse_id=warehouse_id,
                user_id=user_id,
                created_at__month=current_month,
                created_at__year=current_year).aggregate(Sum('amount'))
        storge_bill = amount['amount__sum'] or 0
        data['current_month_bill'] = order_bill + storge_bill

        data['month_bill_list'] = []
        data['month_bill_list'].append(
            {'month': str(current_month), 'bill': data['current_month_bill']})

        data['month_orders_list'] = []
        data['month_orders_list'].append(
            {'month': str(current_month), 'orders': data['current_month_orders']})

        for num in [1, 2]:
            time = timezone.now() + relativedelta(months=-num)
            month = time.month
            year = time.year
            orders = \
                Order.objects.filter(
                    warehouse_id=warehouse_id,
                    user_id=user_id,
                    created_at__month=month,
                    created_at__year=year).count()

            amount = \
                OrderBill.objects.filter(
                    warehouse_id=warehouse_id,
                    user_id=user_id,
                    created_at__month=month,
                    created_at__year=year).aggregate(Sum('amount'))
            order_bill = amount['amount__sum'] or 0
            amount = \
                StorgeBill.objects.filter(
                    warehouse_id=warehouse_id,
                    user_id=user_id,
                    created_at__month=month,
                    created_at__year=year).aggregate(Sum('amount'))
            storge_bill = amount['amount__sum'] or 0
            bill = order_bill + storge_bill

            data['month_orders_list'].append(
                {'month': str(month), 'orders': orders})
            data['month_bill_list'].append(
                {'month': str(month), 'bill': bill})
        result = get_used_warehouse_operation_info(warehouse_id, token)
        if result:
            data['used_time'] = result['used_time']
        return data
