# -*- coding: utf-8 -*-
from django.db import models
from .base import BaseModel


class SysIncrementSequence(BaseModel):
    id = models.AutoField(primary_key=True)
    sequence_type = models.CharField(max_length=20, verbose_name='类型')
    increment_sequence = models.BigIntegerField(verbose_name='序号')

    class Meta:
        db_table = 'sys_increment_sequence'
