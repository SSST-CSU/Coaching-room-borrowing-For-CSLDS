# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
# Create your models here.


class User(models.Model):
    id = models.CharField(primary_key=True, max_length=11)
    name = models.CharField(max_length=10)
    pwd = models.CharField(max_length=20)
    tel = models.CharField(max_length=15)
    mail = models.CharField(max_length=20)

    def __unicode__(self):
        return unicode(self.id + self.name)


class Admin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_admin', primary_key=True)
    level = models.IntegerField()


class BorrowRecord(models.Model):
    applydatetime = models.DateTimeField()
    date = models.DateField()
    time = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_br')
    num = models.IntegerField()
    com = models.CharField(max_length=30, null=True, blank=True)
    usereason = models.CharField(max_length=100)
    # 申请中、同意申请、拒绝申请
    stat = models.CharField(max_length=10, null=True, blank=True)

    def __unicode__(self):
        return unicode(str(self.date) + str(self.time) + str(self.user))


    class Meta:
        unique_together = ('date', 'time', 'user')