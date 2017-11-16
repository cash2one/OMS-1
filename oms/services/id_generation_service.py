# -*- coding: utf-8 -*-
from datetime import datetime
from oms.services.increment_sequence_service import SysIncrementSequenceService


class IdGenerationService(object):
    ORDER_START = 10000000
    STOCK_IN_START = 500000
    STOCK_OUT_START = 100000
    STOCK_TRANSFER_START = 100000
    SKU_START = 10000
    STORE_START = 10000

    @classmethod
    def generate_order_id(cls):
        dt = datetime.today().strftime('%Y%m%d')
        sequence_type = 'od' + dt
        seq_start, _ = SysIncrementSequenceService.get_increment_sequence(
            sequence_type=sequence_type,
            start=cls.ORDER_START
        )
        return sequence_type + str(seq_start)

    @classmethod
    def generate_sku_id(cls, user_id):
        sequence_type = 'sku' + str(user_id)
        seq_start, _ = SysIncrementSequenceService.get_increment_sequence(
            sequence_type=sequence_type,
            start=cls.SKU_START
        )
        return sequence_type + str(seq_start)

    @classmethod
    def generate_stock_in_id(cls):
        dt = datetime.today().strftime('%Y%m%d')
        sequence_type = 'sti' + dt
        seq_start, _ = SysIncrementSequenceService.get_increment_sequence(
            sequence_type=sequence_type,
            start=cls.STOCK_IN_START
        )
        return sequence_type + str(seq_start)

    @classmethod
    def generate_stock_out_id(cls):
        dt = datetime.today().strftime('%Y%m%d')
        sequence_type = 'sto' + dt
        seq_start, _ = SysIncrementSequenceService.get_increment_sequence(
            sequence_type=sequence_type,
            start=cls.STOCK_OUT_START
        )
        return sequence_type + str(seq_start)

    @classmethod
    def generate_stock_transfer_id(cls):
        dt = datetime.today().strftime('%Y%m%d')
        sequence_type = 'stt' + dt
        seq_start, _ = SysIncrementSequenceService.get_increment_sequence(
            sequence_type=sequence_type,
            start=cls.STOCK_TRANSFER_START
        )
        return sequence_type + str(seq_start)

    @classmethod
    def generate_store_id(cls, user_id):
        sequence_type = 'st' + str(user_id)
        seq_start, _ = SysIncrementSequenceService.get_increment_sequence(
            sequence_type=sequence_type,
            start=cls.STORE_START
        )
        return sequence_type + str(seq_start)
