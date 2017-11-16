# -*- coding: utf-8 -*-
from django.db import models
from .base import BaseModel


# 入库单
class StockIn(BaseModel):

    STOCK_IN_TYPE = (
        (1, '普通入库单'),
        (2, '退货入库')
    )

    STOCK_IN_STATUS = (
        ('NEW', '未开始处理'),
        ('ACCEPT', '仓库接单'),
        ('PARTFULFILLED', '部分收货完成'),
        ('FULFILLED', '收货完成'),
        ('EXCEPTION', '异常'),
        ('CANCELED', '取消'),
        ('CLOSED', '关闭'),
        ('REJECT', '拒单'),
        ('CANCELEDFAIL', '取消失败')
    )
    id = models.CharField(
        max_length=20,
        primary_key=True,
        verbose_name='入库单号',
        editable=False)
    # entry_order_code = models.CharField(
    #     max_length=32,
    #     null=False,
    #     verbose_name='入库单编号')

    stock_in_type = models.IntegerField(
        default=1,
        null=False,
        choices=STOCK_IN_TYPE,
        verbose_name='入库单类型')

    stock_in_status = models.CharField(
        max_length=10,
        null=False,
        default='NEW',
        choices=STOCK_IN_STATUS,
        verbose_name='入库单状态')

    entry_order_id = models.CharField(
        max_length=32,
        null=True,
        verbose_name='仓储系统入库单ID')

    # stock_in_code = models.CharField(
    #     max_length=32,
    #     null=False,
    #     verbose_name='入库单编号')

    order_code = models.CharField(
        max_length=32,
        null=False,
        verbose_name='关联订单编号')

    user_note = models.CharField(
        max_length=300,
        null=True,
        verbose_name='卖家备注'
    )

    express = models.CharField(
        max_length=32,
        null=False,
        verbose_name='快递公司')

    # 多个快递单号，使用特殊符号分割开来
    express_number = models.CharField(
        max_length=300,
        null=False,
        verbose_name='快递单号')

    estimated_to_arrival = models.DateTimeField(verbose_name='预计到达时间')

    warehouse_id = models.\
        CharField(max_length=20, null=False, verbose_name='仓库id')

    warehouse_name = models.CharField(max_length=32, verbose_name='仓库名称')

    wms_app_key = models.\
        CharField(max_length=20, verbose_name='wms_app_key', null=True)
    # 背后是否需要有一套的统一仓库编码
    warehouse_code = models.CharField(max_length=32, verbose_name='仓库编码')

    user_id = models.IntegerField(null=False, verbose_name='用户id')
    user_name = models.CharField(default='', max_length=50, null=True, verbose_name='客户名称')

    user_mobile = models.CharField(max_length=32, verbose_name='用户手机号')

    sender_phone = models.CharField(max_length=50, verbose_name='发货人电话', null=True)
    sender_name = models.CharField(max_length=50, verbose_name='发货人姓名', null=True)
    recipient_phone = models.CharField(max_length=50, verbose_name='收件人电话', null=True)
    recipient_name = models.CharField(max_length=50, verbose_name='收件人姓名', null=True)

    # out_biz_code = models.CharField(max_length=30, verbose_name='外部业务编码')

    class Meta:
        app_label = 'oms'
        db_table = 'stock_in'
        ordering = ['-created_at']
