from django.contrib import admin

from machine import models


# Register your models here.
@admin.register(models.Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ('title',)


@admin.register(models.Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = ('machine',)


@admin.register(models.CustomerService)
class CSAdmin(admin.ModelAdmin):
    list_display = ('content', 'wechat', )

