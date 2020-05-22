from django.contrib import admin as a

# Register your models here.
from news import models as nsm
# Content, Record


# @admin.register(nsm.Content)
# class NewsAdmin(admin.ModelAdmin):
#     list_display = ('title',)
#
#
# @admin.register(nsm.Record)
# class NewsRecordAdmin(admin.ModelAdmin):
#     list_display = ('user', 'news',)


@a.register(nsm.News)
class NewsAdmin(a.ModelAdmin):
    list_display = ('title', )
