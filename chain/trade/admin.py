from django.contrib import admin

# Register your models here.
from trade import models


# @admin.register(Trade)
# class TradeAdmin(admin.ModelAdmin):
#     list_display = ('type', 'status',)

@admin.register(models.Sell)
class SellAdmin(admin.ModelAdmin):
    list_display = ('serial_no', 'number', )


@admin.register(models.Buy)
class BuyAdmin(admin.ModelAdmin):
    list_display = ('serial_no', 'number', )


@admin.register(models.SellRecord)
class SellRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'serial_no', )


@admin.register(models.BuyRecord)
class BuyRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'buy', )


@admin.register(models.TPrice)
class PriceAdmin(admin.ModelAdmin):
    list_display = ('price',)
