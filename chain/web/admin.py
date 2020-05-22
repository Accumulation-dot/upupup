from django.contrib import admin

# Register your models here.

from web.models import AppVersion

@admin.register(AppVersion)
class AppVersionAdmin(admin.ModelAdmin):
    list_display = ('version',)