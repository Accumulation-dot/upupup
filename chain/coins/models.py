from django.db import models

from django.db.models import Sum

from user import models as users

from datetime import datetime
from tools import choices


# Create your models here.

class Record(models.Model):
    user = models.ForeignKey(users.CoinUser, on_delete=models.CASCADE,
                             verbose_name='用户ID', help_text='用户ID')
    key = models.CharField(max_length=20)
    # 可以是正可以是负 正表示收入 负表示支出
    point = models.FloatField(verbose_name='获取的数量')
    shop = models.FloatField(verbose_name='必须用来购物的部分，系统获得', default=0)
    datetime = models.DateTimeField(auto_now_add=True)
    desc = models.CharField(max_length=120, default='', null=False,
                            verbose_name='说明', help_text='说明')

    class Meta:
        verbose_name = '货币获取的记录'
        verbose_name_plural = verbose_name


def register_record(user, point=1):
    record = Record(user=user, point=point, desc='注册奖励')
    record.save()
    while True:
        info = users.CoinUserInfo.objects.filter(user=user.id).first()
        num = info.coin
        result = users.CoinUserInfo.objects.filter(user=user.id, coin=num).update(coin=num + point)
        if result == 0:
            continue
        break
    return record


freq_choices = ((0, '有限次数'), (1, '每天次数'), (2, '每月的次数'), (3, '每年的次数'), (4, '未限制次数'))


class Award(models.Model):
    key = models.CharField(max_length=50, unique=True, verbose_name='奖励的key', help_text='奖励的key 根据key进行搜索是否有存在',
                           choices=choices.award_choices)
    coin = models.FloatField(verbose_name='奖励的分数', help_text='奖励或者需要扣除')
    percent = models.FloatField(verbose_name='必须用来购物的部分', help_text='必须用来购物的百分比', default=0.0)
    type = models.IntegerField(verbose_name='奖励的类型', help_text='奖励的类型')
    freq = models.IntegerField(choices=freq_choices, default=0, verbose_name='频率', help_text='频率')
    freq_num = models.IntegerField(default=1, verbose_name='次数', help_text='次数')
    desc = models.CharField(max_length=30, verbose_name='奖励的描述', help_text='奖励的描述')

    class Meta:
        verbose_name = '奖励类型'
        verbose_name_plural = verbose_name


class CoinRule(models.Model):
    name = models.CharField(max_length=20, verbose_name='规则名', default='规则', )
    min_num = models.FloatField(verbose_name='剩余的最小值', default=0)
    tax = models.FloatField(verbose_name='出售的税', help_text='手续费 百分比', default=0.25)
    pay = models.BooleanField(verbose_name='是否需要支付', help_text='是否需要支付金额, 手动去控制', default=0)
    shop = models.FloatField(verbose_name='获取币的购物百分比', help_text='获取的币 多少需要进行购物, 最大是1最小是0', default=0.15)
    advert = models.FloatField(default=1.0, verbose_name='发布消耗', help_text='发布需要消耗')
    used = models.BooleanField(verbose_name='是否已经启用', default=False, )

    class Meta:
        verbose_name = verbose_name_plural = '规则表'


def query_coin(user):
    coins = Record.objects.filter(user=user).aggregate(sum=Sum("point"))
    if coins is None or coins.get('sum') is None:
        return 0.0
    return int(coins.get('sum', 0) * 1000) / 1000.0


def query_shop(user):
    coins = Record.objects.filter(user=user).aggregate(sum=Sum("shop"))
    if coins is None or coins.get('sum') is None:
        return 0.0
    return int(coins['sum'] * 1000) / 1000.0


def query_award(key, user):
    if key is None:
        return
    awards = Award.objects.filter(key=key)
    if awards is None:
        return 0

    for award in awards:
        now = datetime.now()
        shop = award.coin * max(0, min(1, award.percent))
        point = award.coin - shop
        records = Record.objects.filter(user=user, key=key, )
        record = Record(user=user, key=key, point=point, shop=shop, desc=award.desc)
        if award.freq == 4:
            record.save()
            return
        elif award.freq == 1:
            records = records.filter(datetime__day=now.date())
        elif award.freq == 2:
            records = records.filter(datetime__year=now.year, datetime__month=now.month)
        elif award.freq == 3:
            records = records.filter(datetime__year=now.year)
        if records.count() < award.freq_num:
            record.save()


def query_rule():
    rul = CoinRule.objects.filter(used=True).first()
    if rul is not None:
        return rul
    return CoinRule()


def record_creation(user, key, point, desc, shop=0):
    r = Record(user=user, key=key, point=point, desc=desc, shop=shop)
    r.save()
    return r
