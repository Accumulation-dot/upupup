from django.db import models

# Create your models here.
from tools.base import BaseModel


class AppVersion(BaseModel):

    app = models.FileField(upload_to='app/',
                           default='app-release.apk', verbose_name='apk', help_text='apk 文件', )
    version = models.TextField(verbose_name='版本', default='1.0.0')

    flag = models.BooleanField(default=True, verbose_name='是否强制更新', help_text='是否强制更新 应该是强制更新')



    def __str__(self):
        return '版本'

    class Meta:
        verbose_name = verbose_name_plural = '版本更新'
        ordering = ('-created',)
