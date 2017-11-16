# -*- coding: UTF-8 -*-
from django.db import models
from oms.models.base import BaseModel


class Order(BaseModel):

    # choices
    '''
    ORDER_STATUS_CHOICES = (
        (10, '待付款'),
        (20, '已付款'),
        (30, '已发货'),
        (40, '已确认收货'),
        (50, '已完成'),
        (60, '已关闭')
    )
    '''
    ORDER_STATUS_CHOICES = (
        (10, '未审核'),
        (20, '已审核'),
        (30, '发货完成'),
        (40, '已签收'),
        (50, '订单取消'),
        (60, '订单删除'),
        (70, '已拆单'),
        (80, '发送wms失败')
    )

    # 出库单状态(NEW-未开始处理;
    # ACCEPT-仓库接单;
    # PARTDELIVERED-部分发货完成;
    # DELIVERED-发货完成;
    # EXCEPTION-异 常;
    # CANCELED-取消;
    # CLOSED-关闭;
    # REJECT-拒单;
    # CANCELEDFAIL-取消失败;只传英文编码)

    WMS_STATUS_CHOICE = (
        ('NEW', '未开始处理'),
        ('ACCEPT', '仓库接单'),
        ('PARTDELIVERED', '部分发货完成'),
        ('DELIVERED', '发货完成'),
        ('EXCEPTION', '异常'),
        ('CANCELED', '取消'),
        ('CLOSED', '关闭'),
        ('REJECT', '拒单'),
        ('CANCELEDFAIL', '取消失败'),
    )

    ORDER_MARK_CHOICE = (
        (10, '正常'),
        (20, '待自动审核'),
        (30, '待人工审核'),
        (40, '锁定')
    )
    REFUND_STATUS_CHOICES = (
        (0, '没有退款'),
        (1, '退款中'),
        (2, '退款成功'),
        (3, '退款关闭')
    )
    PAYMENT_TYPE = (
        (1, '在线支付'),
        (2, '货到付款')
    )
    #
    # ORDER_STATES = (
    #     RawState,
    #     SyncState,
    #     UnCheckState,
    #     CheckedState,
    #     UnDistributeState,
    #     DistributedState,
    #     LockedState
    # )
    # 状态
    # order_state = FSMField(
    # default=ORDER_STATUS_CHOICES[0], choices=ORDER_STATUS_CHOICES)
    id = models.CharField(
        max_length=20,
        primary_key=True,
        verbose_name='order单号',
        editable=False)

    order_status = models.IntegerField(
        default=10,
        null=False,
        choices=ORDER_STATUS_CHOICES,
        verbose_name='订单状态值')

    order_status_info = models.CharField(
        default='原始状态',
        max_length=10,
        null=False,
        verbose_name='订单状态描述')

    status_ori = models.CharField(max_length=20, verbose_name='原始状态')

    refund_status_ori = models.IntegerField(
        default=10,
        choices=REFUND_STATUS_CHOICES,
        verbose_name='电商平台的退款信息')

    wms_status = models.CharField(
        max_length=10,
        default='NEW',
        choices=WMS_STATUS_CHOICE,
        verbose_name='仓库的处理状态')

    order_mark = models.IntegerField(
        default=10,
        choices=ORDER_MARK_CHOICE,
        verbose_name='订单标签')

    mark_reason = models.CharField(
        max_length=50,
        null=True,
        verbose_name='锁定或者转人工处理的原因说明')
    # 订单信息
    order_type = models.IntegerField(null=True, verbose_name='订单类型')
    order_type_info = models.CharField(
        max_length=32,
        null=True,
        verbose_name='订单类型描述')

    # 订单编号丨平台店铺 丨 付款时间 丨是否货到付款
    order_code = models.CharField(
        max_length=32,
        null=False,
        verbose_name='订单编号')
    store_name = models.CharField(
        max_length=32,
        null=True,
        verbose_name='店铺名称')

    user_id = models.IntegerField(null=False, verbose_name='用户id')
    user_name = models.CharField(default='', null=True,
                                 max_length=50, verbose_name='客户名称')
    store = models.ForeignKey('oms.Store', null=True)

    # 买家昵称丨 收货人姓名丨 电话丨省丨市丨区丨邮编丨详细地址丨买家备注丨卖家备注丨订单金额丨发票内容丨发票抬头丨订单类型
    # 用户信息
    user_nickname = models.CharField(
        max_length=32,
        null=True,
        verbose_name='卖家昵称'
    )
    buyer_nickname = models.CharField(
        max_length=32,
        null=True,
        verbose_name='买家昵称'
    )
    buyer_note = models.CharField(
        max_length=300,
        null=True,
        verbose_name='买家留言'
    )
    user_note = models.CharField(
        max_length=300,
        null=True,
        verbose_name='卖家备注'
    )
    trade_type = models.IntegerField(
        default=0,
        null=True,
        verbose_name='交易类型'
    )
    total_price = models.FloatField(default=0, null=True, verbose_name='总价格')
    goods_price = models.FloatField(default=0, null=True, verbose_name='商品价格')
    discount_fee = models.FloatField(default=0, null=True, verbose_name='折扣价格')
    quantity = models.IntegerField(default=0, null=True, verbose_name='商品数量')

    # 交易信息
    trade_no = models.CharField(max_length=32, null=True, verbose_name='交易单号')
    trade_from = models.IntegerField(default=0, null=True, verbose_name='交易来源')
    trade_type = models.IntegerField(default=0, null=True, verbose_name='交易类型')
    invoice = models.CharField(max_length=32, null=True, verbose_name='发票内容')
    invoice_header = models.CharField(
        max_length=32,
        null=True,
        verbose_name='发票抬头')

    payment = models.FloatField(default=0, null=True, verbose_name='支付金额')
    payment_type = models.IntegerField(
        default=0,
        choices=PAYMENT_TYPE,
        null=True,
        verbose_name='支付方式')
    # 客户名称丨仓妈咪ID丨下单时间丨快递公司丨快递单号
    express_number = models.CharField(
        max_length=32,
        null=True,
        verbose_name='快递编号'
    )
    express = models.CharField(max_length=20, null=True, verbose_name='快递公司')
    express_note = models.CharField(
        max_length=50,
        null=True,
        verbose_name='快递留言'
    )
    express_fee = models.FloatField(default=0, null=True, verbose_name='快递费用')
    zip_code = models.CharField(max_length=32, null=True, verbose_name='邮政编码')
    # 商品名称丨 商品规格 丨商家编码丨 商品条码丨 商品总数（个）丨订单重量
    # 拣货员丨拣货时间丨打印时间丨打印员丨包装时间丨包装员丨验货时间丨验货员丨发货状态丨耗材条码丨耗材名称

    # 状态
    # order_state = FSMField(default=ORDER_STATUS_CHOICES[0], choices=ORDER_STATUS_CHOICES)
    # order_status = models.IntegerField(null=True, verbose_name='订单状态值')
    # order_status_info = models.CharField(max_length=10, null=True, verbose_name='订单状态描述')

    # 时间信息
    pay_time = models.DateTimeField(null=True, verbose_name='支付时间')
    add_time = models.DateTimeField(null=True, verbose_name='下单时间')
    operate_time = models.DateTimeField(null=True, verbose_name='审核时间')
    # 用户信息
    # user_nickname = models.CharField(
    #     max_length=32,
    #     null=True,
    #     verbose_name='卖家昵称')
    # buyer_nickname = models.CharField(
    #     max_length=32,
    #     null=True,
    #     verbose_name='买家昵称')
    # buyer_note = models.CharField(
    #     max_length=300,
    #     null=True,
    #     verbose_name='买家留言')
    # user_note = models.CharField(
    #     max_length=300,
    #     null=True,
    #     verbose_name='卖家备注')

    # 锁定
    is_locked = models.BooleanField(default=False)
    # 合并订单
    is_tobe_combine = models.BooleanField(default=False)
    # 该订单是否合并，如果合并，查找合并订单
    is_combined = models.BooleanField(default=False)
    # 该订单是否拆单，如果拆单，查找SplitOrder
    is_splited = models.BooleanField(default=False)

    # 收货信息
    consignee_name = models.CharField(
        max_length=20,
        null=True,
        verbose_name='收货人姓名')
    consignee_country = models.CharField(
        max_length=20,
        null=True,
        verbose_name='收货人国籍')
    consignee_province = models.CharField(
        max_length=32,
        null=True,
        verbose_name='收货人省份')
    consignee_city = models.CharField(
        max_length=32,
        null=True,
        verbose_name='收货城市')
    consignee_area = models.CharField(
        max_length=32,
        null=True,
        verbose_name='收货区域')
    consignee_detail = models.CharField(
        max_length=50,
        null=True,
        verbose_name='收货详细地址')
    consignee_receiver_zip = models.CharField(
        max_length=10,
        null=True,
        verbose_name='收货人邮编')
    consignee_town = models.CharField(
        max_length=32,
        null=True,
        verbose_name='收货人街道地址')
    consignee_phone = models.CharField(
        max_length=22,
        null=True,
        verbose_name='收货人电话')

    # 默认仓库信息
    # sender_phone = models.CharField(
    #     max_length=50, verbose_name='发货人电话', null=True)
    # sender_name = models.CharField(
    #     max_length=50, verbose_name='发货人姓名', null=True)

    warehouse_id = models.CharField(
        max_length=20,
        null=True,
        verbose_name='仓库id')
    warehouse_name = models.CharField(
        max_length=32,
        null=True,
        verbose_name='仓库名称')
    warehouse_code = models.CharField(
        max_length=32,
        null=True,
        verbose_name='wms仓库编码')
    wms_app_key = models.CharField(
        max_length=20,
        verbose_name='wms_app_key',
        null=True)
    warehouse_province = models.CharField(
        max_length=32,
        null=True,
        verbose_name='warehouse省份')
    warehouse_city = models.CharField(
        max_length=32,
        null=True,
        verbose_name='warehouse城市')
    warehouse_area = models.CharField(
        max_length=32,
        null=True,
        verbose_name='warehouse区域')
    warehouse_detail = models.CharField(
        max_length=50,
        null=True,
        verbose_name='warehouse收货详细地址')

    warehouse_recipient_name = models.CharField(
        max_length=20,
        null=True,
        verbose_name='warehouse收件人姓名')

    warehouse_recipient_contact = models.CharField(
        max_length=30,
        null=True,
        verbose_name='warehouse收件人电话')

    # 仓库推荐的快递公司和编码

    logistics_name = models.\
        CharField(max_length=20, null=True, verbose_name='快递公司名称')
    logistics_code = models.\
        CharField(max_length=20, null=True, verbose_name='快递公司编码')

    # delivery_order_id = models.CharField(
    #     max_length=32,
    #     null=True,
    #     verbose_name='仓库发货单')
    # 关联信息
    # consignee = models.ForeignKey('oms.Consignee', null=True)
    # store_id = models.CharField(verbose_name='店铺标识')
    # user_id = models.CharField(verbose_name='用户标识')
    # user = models.ForeignKey('oms.User', null=True)
    delivery_order_id = models.CharField(
        max_length=30,
        verbose_name='出库单仓储系统编码')

    class Meta:
        ordering = ['-created_at']
