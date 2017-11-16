# -*- coding: utf-8 -*-
from django.db.models import Prefetch
from django.core.paginator import Paginator
from oms.models.sku_warehouse import SkuWarehouse
from oms.models.sku import Sku


def stock_check(sku, bar_code, sku_name, page_size, page_index):
    try:
        sku_set = Sku.objects.all()
        stock = SkuWarehouse.objects.prefetch_related(Prefetch('sku_set', queryset=sku_set, to_attr='sku_set'))
        if sku:
            stock = stock.filter(sku=sku)
        if bar_code:
            stock = stock.filter(bar_code=bar_code)
        if sku_name:
            stock = stock.filter(sku_name=sku_name)

        paginator = Paginator(stock, page_size)
        rows = paginator.page(page_index)
        tmp = []
        for row in rows:
            tmp.append({
                        # 'id': row.id,
                        'sku_name': row.sku.sku_name,
                        'specification': row.sku.specification,
                        'sku_code': row.sku.bar_code,
                        'seller_id': row.sku.user_id,
                        'quantity': row.sku.available_quantity,
                        })
        total = paginator.count
        result = {'rows': tmp, 'total': total}
        return result
    except Exception as e:
        print(e)
        return None
