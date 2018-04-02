# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from models import *
# Register your models here.


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'pwd')


class BorrowRecordAdmin(admin.ModelAdmin):
    list_display = ('date', 'time', 'user', 'stat')
    search_fields=('date', 'time', 'user', 'stat')


class AdminAdmin(admin.ModelAdmin):
    list_display = ('user',)


admin.site.register(User, UserAdmin)
admin.site.register(BorrowRecord, BorrowRecordAdmin)
admin.site.register(Admin, AdminAdmin)
admin.site.site_header = '学服活动室借用系统'
admin.site.site_title = '学服活动室借用系统'


