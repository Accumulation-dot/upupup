import time
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
from django.db.models import Count, Q

from tools.base import BaseModel
from tools import random


class CoinUser(AbstractUser):
    qq = models.CharField('qq 号码', max_length=20, blank=True)

    wechat = models.CharField('微信号码', max_length=40, blank=True)

    level = models.PositiveSmallIntegerField(default=1, choices=((0, '管理员'), (1, '普通用户'), (2, 'v1用户')),
                                             verbose_name='等级', help_text='等级')

    code = models.CharField(max_length=20, verbose_name='邀请码', help_text='唯一邀请码', default=random.unique_key)

    inviter = models.CharField(max_length=20, verbose_name='邀请者码', default='', help_text='邀请者', null=True, blank=True)

    class Meta:
        verbose_name = verbose_name_plural = '用户表'

    def __str__(self):
        return self.username


class CoinUserInfo(BaseModel):
    user = models.OneToOneField(CoinUser, on_delete=models.DO_NOTHING)

    name = models.CharField(max_length=20, blank=True, default='',
                            verbose_name='用户名称', help_text='用户名称 需要完善信息')

    address = models.UUIDField(max_length=100, blank=False, default=uuid.uuid5(uuid.NAMESPACE_DNS, str(uuid.uuid1())),
                               verbose_name='地址', help_text='地址', )

    class Meta:
        verbose_name = verbose_name_plural = "用户信息表"

    def __str__(self):
        return self.user.username + ' &&' + self.name


class Address(BaseModel):
    user = models.OneToOneField(CoinUser, on_delete=models.DO_NOTHING)
    address = models.CharField(max_length=100, verbose_name='唯一的表示地址')

    class Meta:
        verbose_name = verbose_name_plural = '用户标示表'

    def __str__(self):
        return self.user.username + ' &&' + self.name


class Identifier(models.Model):
    user = models.OneToOneField(CoinUser, on_delete=models.DO_NOTHING,
                                verbose_name='用户信息', help_text='用户信息')
    name = models.CharField(max_length=20,
                            verbose_name='姓名', help_text='用户信息')
    number = models.CharField(max_length=20,
                              verbose_name='ID', help_text='用户身份证信息')

    class Meta:
        verbose_name = verbose_name_plural = '身份证信息'
        unique_together = ('number',)

        def __str__(self):
            return self.user.username + ' &&' + self.name


def user_info_creation(user):
    info = CoinUserInfo(user=user, name=user.username)
    info.save()
    return info


def user_address_creation(user):
    u = uuid.uuid5(uuid.NAMESPACE_DNS, str(uuid.uuid1()))

    address = Address(user=user, address=str(u) + str(int(time.time())))
    address.save()
    return address


def ident_count(user):
    return Identifier.objects.aggregate(count=Count('id', filter=Q(user=user))).get('count', 0)


def inviter_query(user):
    print(user.inviter)
    inviter = CoinUser.objects.filter(code=user.inviter).first()
    print(inviter)
    return inviter
    #CoinUser.objects.filter(code=user.inviter).first()
