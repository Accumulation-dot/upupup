from django.db import models


# Create your models here.
from tools.base import BaseModel


class AppVersion(BaseModel):
    version = models.TextField(verbose_name='版本', default='0.0.0')

    flag = models.BooleanField(default=True, verbose_name='update_flat', help_text='是否强制更新 应该是强制更新')

    class Meta:
        verbose_name = verbose_name_plural = '版本更新'
        ordering = ('-created',)
