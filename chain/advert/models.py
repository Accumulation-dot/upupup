from django.db import models
from user import models as users


# Create your models here.

# 广告内容 发布广告内容需要进行币的删除

class Content(models.Model):
    user = models.ForeignKey(users.CoinUser, on_delete=models.CASCADE, verbose_name='用户信息', related_name='发布者')
    title = models.CharField(max_length=60, verbose_name='标题', help_text='标题')
    img = models.ImageField(upload_to='advert/content/', help_text='图片', default=None)
    content = models.CharField(max_length=400, default='', blank=True, verbose_name='广告内容', help_text='广告内容')
    readers = models.ManyToManyField(users.CoinUser, through='Record', related_name='阅读者')

    datetime = models.DateTimeField(auto_now=True, verbose_name='创建日期', help_text='创建时间')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '广告表'
        verbose_name_plural = verbose_name
        ordering = ('-datetime',)


class Record(models.Model):
    user = models.ForeignKey(users.CoinUser, on_delete=models.CASCADE, verbose_name='用户', related_name='读者')

    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='新闻', )

    datetime = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '新闻表'
        verbose_name_plural = verbose_name
        ordering = ['id']
