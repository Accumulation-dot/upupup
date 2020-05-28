from django.contrib import admin

# Register your models here.
from pay.models import Pay


@admin.register(Pay)
class PayAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'number',)
