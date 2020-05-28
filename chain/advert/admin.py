from django.contrib import admin

# Register your models here.
from advert.models import Content


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ('user', 'title',)
