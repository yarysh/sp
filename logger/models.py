# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class SMSLog(models.Model):
    phone = models.CharField(max_length=64, null=True, blank=True)
    text = models.CharField(max_length=64, null=True, blank=True)
    payload = models.CharField(max_length=512)
    success = models.BooleanField()
    created = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sms_logs'
