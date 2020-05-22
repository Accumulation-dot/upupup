from django.contrib import admin

from coins.models import Award, CoinRule

from coins import models

# Register your models here.

@admin.register(Award)
class AwardAdmin(admin.ModelAdmin):
    list_display = ('key', 'coin', 'percent',)


@admin.register(CoinRule)
class CoinRuleAdmin(admin.ModelAdmin):
    list_display = ('name', )


@admin.register(models.Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'key', )
