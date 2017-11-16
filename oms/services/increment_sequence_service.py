# -*- coding:utf-8 -*-
from oms.models.sys_increment_sequence import SysIncrementSequence
from django.db import transaction
import random


class SysIncrementSequenceService(object):

    @staticmethod
    def create(sequence_type, start):
        obj = SysIncrementSequence.objects.create(sequence_type=sequence_type,
                                                  increment_sequence=start)
        return obj

    @staticmethod
    def get_increment_sequence(sequence_type, range=0, start=10000000):

        with transaction.atomic(using="default"):
            try:
                obj = SysIncrementSequence.objects.\
                    get(sequence_type=sequence_type)
            except SysIncrementSequence.DoesNotExist or\
                    SysIncrementSequence.MultipleObjectsReturned:
                obj = SysIncrementSequenceService.create(
                    sequence_type=sequence_type, start=start)

            try:
                increment_sequence = obj.increment_sequence
                obj.increment_sequence = increment_sequence + 1 + range
                obj.save()
                return increment_sequence + 1, increment_sequence + 1 + range
            except Exception as e:
                return random.randint(start, start + 100000000)
