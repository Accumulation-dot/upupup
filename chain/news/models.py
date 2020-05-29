from django.db import models

# Create your models here.
from user.models import CoinUser

from tools.random import uuid_key


# class Content(models.Model):
#     title = models.CharField(max_length=60, verbose_name='标题', help_text='标题')
#     img = models.CharField(max_length=256, default='', blank=True, verbose_name='图片', help_text='图片')
#     url = models.CharField(max_length=256, default='', blank=True, verbose_name='文章链接', help_text='文章链接')
#
#     readers = models.ManyToManyField(CoinUser, through='Record', related_name='readers')
#
#     datetime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
#
#     def __str__(self):
#         return self.title
#
#     class Meta:
#         verbose_name = '新闻表'
#         verbose_name_plural = verbose_name
#         ordering = ['-datetime']
#
#
# class Record(models.Model):
#     user = models.ForeignKey(CoinUser, on_delete=models.CASCADE, related_name='user',
#                              verbose_name='用户', help_text='用户ID')
#     news = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='news',
#                              verbose_name='新闻', help_text='新闻id')
#     datetime = models.DateTimeField(auto_now=True,
#                                     verbose_name='时间', help_text='记录的时间')
#     address = models.GenericIPAddressField(null=True)
#
#     def __str__(self):
#         return self.user.username + self.news.title
#
#     class Meta:
#         verbose_name = '新闻观看记录'
#         verbose_name_plural = verbose_name


class News(models.Model):
    id = models.UUIDField(default=uuid_key, primary_key=True)

    img = models.ImageField(upload_to='news/img/')

    title = models.CharField(max_length=50, help_text='标题')

    url = models.URLField(help_text='文章链接')

    date = models.DateField(auto_now_add=True, null=True)

    created = models.DateTimeField(auto_now=True,)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = verbose_name_plural = '新闻表'
        ordering = ('-created',)


class Task(models.Model):
    user = models.ForeignKey(CoinUser, on_delete=models.DO_NOTHING, related_name='user')

    date = models.DateField(auto_now_add=True, null=True)

    earn = models.FloatField(help_text='奖励金额', default=0)

    class Meta:
        verbose_name = verbose_name_plural = '任务'
        unique_together = ('user', 'date')
