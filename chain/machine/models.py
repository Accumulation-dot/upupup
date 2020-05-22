import time
import datetime

from django.db import models
from django.db.models import Count, Q, Sum

from tools.base import BaseModel
from user import models as um
from tools import random

# Create your models here.


class Machine(models.Model):
    title = models.CharField(max_length=20, unique=True,
                             verbose_name='标题', help_text='标题')

    days = models.PositiveSmallIntegerField(verbose_name='天数', help_text='需要的天数', default=30)

    number = models.FloatField(verbose_name='产出', help_text='产出的数量', default=0)

    append = models.PositiveIntegerField(default=0, verbose_name='days_append', help_text='每次购买需要增加的天数 但是总产出不变')

    users = models.ManyToManyField(um.CoinUser, through='Record')

    cost = models.FloatField(verbose_name='花费', help_text='需要的花费', default=0)

    s_no = models.CharField(max_length=100, default=random.machine_code)

    max_count = models.PositiveSmallIntegerField(verbose_name='限制数量', default=0, help_text='0为不限制数量')

    given = models.BooleanField(default=False, help_text='是否是赠送项', verbose_name='赠送')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '矿机表'
        verbose_name_plural = verbose_name


class Record(BaseModel):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='machine')
    user = models.ForeignKey(um.CoinUser, on_delete=models.CASCADE, related_name='users')
    days = models.IntegerField(verbose_name='天数', default=0)
    number = models.FloatField(verbose_name='days_earn', default=0)
    expired = models.DateTimeField()

    class Meta:
        verbose_name = '矿机租赁列表'
        verbose_name_plural = verbose_name


class CustomerService(BaseModel):

    content = models.CharField(max_length=100)

    wechat = models.CharField(max_length=80)

    class Meta:
        verbose_name = verbose_name_plural = '客服联系方式'


def machine_given_free(user):
    machine = Machine.objects.filter(given=True).first()
    if machine is not None:
        expired = datetime.datetime.now() + datetime.timedelta(days=machine.days)
        record = Record(user=user, machine=machine, days=machine.days, number=machine.number / machine.days, expired=expired)
        record.save()


def machine_rent_count(user):
    now = datetime.datetime.now()
    return Record.objects.filter(user=user, expired__gte=now)\
        .aggregate(sum=Sum('number')).get('sum', 0)


def machine_earn_count(user):
    now = datetime.datetime.now()
    query = Record.objects.filter(user=user, expired__gte=now).aggregate(sum=Sum('number'))
    result = query.get('sum')
    if result is None:
        return 0
    return result
