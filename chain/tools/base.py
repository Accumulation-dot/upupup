from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True, verbose_name='created_time',
                                   help_text='创建日期', null=True)

    class Meta:
        abstract = True