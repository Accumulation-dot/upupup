import datetime

from django.db import models
from django.db import models as m
from django.db.models import Sum
from django.utils import timezone

from tools import choices
from tools import random
from tools.base import BaseModel
from tools.choices import trade_status
from user import models as um
from user.models import CoinUser, CoinUserInfo


# 用户出售表
class Sell(BaseModel):
    number = models.FloatField(verbose_name='交易的数量总量')
    user = models.ForeignKey(CoinUser, on_delete=models.CASCADE,
                             verbose_name='用户', help_text='用户')
    status = models.PositiveSmallIntegerField(verbose_name='状态', help_text='状态',
                                              choices=trade_status, default=0)
    serial_no = models.CharField(max_length=50, default=random.sell_code, unique=True)

    price = models.PositiveIntegerField(default=0, verbose_name='sell_price', help_text='出售单价')
    # date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.serial_no

    class Meta:
        verbose_name = verbose_name_plural = '出售表'
        ordering = ['-created']


# 用户收购表
class Buy(BaseModel):
    number = models.FloatField(verbose_name='交易的数量总量')
    user = models.ForeignKey(CoinUser, on_delete=models.CASCADE,
                             verbose_name='用户', help_text='用户')
    status = models.PositiveSmallIntegerField(verbose_name='状态', help_text='状态',
                                              choices=trade_status, default=0)
    serial_no = models.CharField(max_length=50, default=random.buy_code, unique=True)
    price = models.PositiveIntegerField(default=0, verbose_name='buy_price', help_text='收购单价')
    # date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = verbose_name_plural = '收购表'
        ordering = ['-created']

    def __str__(self):
        return self.number


class SellRecord(BaseModel):
    user = models.ForeignKey(CoinUser, related_name='buyer', on_delete=models.CASCADE,
                             verbose_name='提交者', help_text='出售者')
    sell = models.ForeignKey(Sell, related_name='sell', on_delete=models.CASCADE,
                             verbose_name='sell', help_text='相关订单')
    status = models.PositiveSmallIntegerField(verbose_name='状态', choices=choices.sell_status, default=0)
    serial_no = models.CharField(max_length=50, default=random.sell_record_code)

    class Meta:
        verbose_name = verbose_name_plural = '预定出售记录'

    def __str__(self):
        return self.serial_no

# Pay.objects.aggregate(count=Count('id', filter=Q(use=True) & Q(user=user)))
# def sell_record_count(sell):
#     return SellRecord.objects.aggregate(count=Count('id', filter=Q(status)))


class BuyRecord(BaseModel):
    user = models.ForeignKey(CoinUser, related_name='seller', on_delete=models.CASCADE,
                             verbose_name='提交者', help_text='出售者')

    buy = models.ForeignKey(Buy, related_name='buy', on_delete=models.CASCADE,
                            verbose_name='buy', help_text='相关订单')
    status = models.PositiveSmallIntegerField(verbose_name='状态', choices=choices.buy_status, default=0)
    serial_no = models.CharField(max_length=50, default=random.buy_record_code)

    class Meta:
        verbose_name = verbose_name_plural = '预定求购记录'

    def __str__(self):
        return self.serial_no


class SellDetail(BaseModel):
    record = models.ForeignKey(SellRecord, on_delete=models.CASCADE,
                               verbose_name='record_id', help_text='出售记录')
    # order = models.CharField(max_length=50,)
    img = models.ImageField(upload_to='sell/order/detail/', help_text='图片', default=None)

    class Meta:
        verbose_name = verbose_name_plural = '出售完善的信息'


class BuyDetail(BaseModel):
    record = models.OneToOneField(BuyRecord, on_delete=models.CASCADE,
                                  verbose_name='record_id', help_text='出售记录')
    # order = models.CharField(max_length=50, )

    img = models.ImageField(upload_to='buy/order/detail/', default=None, null=True, help_text='图片')

    class Meta:
        verbose_name = verbose_name_plural = '收购完善的信息'


class Trade(BaseModel):

    # created 创建时间 即为交易成

    date = models.DateField(auto_now_add=True, null=True)

    price = models.FloatField(help_text='单价', verbose_name='price', default=0)

    count = models.FloatField(help_text='数量', verbose_name='count', default=0)

    total = models.FloatField(verbose_name='total_price', help_text='总价', default=0)

    class Meta:
        verbose_name = verbose_name_plural = '成交的交易记录'


def trade_creation(price, count):
    t = Trade(price=price, count=count, total=price * count)
    t.save()
    return t


# 发布的信息
class Deal(BaseModel):
    user = m.ForeignKey(um.CoinUser, on_delete=m.DO_NOTHING, verbose_name='发布者', help_text='发布者')

    count = m.IntegerField(verbose_name='数量', help_text='发布的数量')

    # created 发布时间

    status = m.IntegerField(verbose_name='状态', help_text='当前状态')

    flag = m.BooleanField(verbose_name='类型', help_text='是否是出售订单, yes 为出售订单， no为收购订单')

    price = m.FloatField(verbose_name='价格', help_text='标记价格')

    serial = m.CharField(max_length=50, default=random.deal_code, verbose_name='订单号', help_text='订单号, 自动生成')

    class Meta:
        verbose_name = verbose_name_plural = '交易'


class Order(BaseModel):

    user = m.ForeignKey(um.CoinUser, on_delete=m.DO_NOTHING, verbose_name='下单者', help_text='下单者')

    flag = m.BooleanField(default=False, verbose_name='标记', help_text='标记')

    deal = m.ForeignKey(Deal, on_delete=m.DO_NOTHING, verbose_name='商品', help_text='有关的发布信息')

    serial = m.CharField(max_length=50, default=random.deal_code, verbose_name='订单号', help_text='订单号, 自动生成')

    # 0 已下单 1 已付款 2 完成 3 投诉 4 取消
    status = m.PositiveSmallIntegerField(verbose_name='状态', help_text='状态')

    class Meta:
        verbose_name = verbose_name_plural = '订单'


class TPrice(BaseModel):

    price = m.FloatField(default=0.03, verbose_name='价格', help_text='参考价格 手动填写')

    t_updated = m.DateField(auto_now=True,)

    class Meta:
        verbose_name = verbose_name_plural = '当日参考价格'


def today_price():
    today = datetime.datetime.now().date()

    price_t = TPrice.objects.all().first()
    if price_t is None:
        price_t = TPrice()
        price_t.save()
        return price_t.price
    elif price_t.t_updated != today:
        yesterday = today - datetime.timedelta(days=1)
        sum2 = Trade.objects.filter(date=yesterday).aggregate(sum=Sum('total'))
        count = Trade.objects.filter(date=yesterday).aggregate(sum=Sum('count'))
        sum_q = sum2.get('sum')
        count_q = count.get('sum')
        if sum_q is not None and count_q is not None:
            price = sum_q / count_q
            price_t.price = price
        price_t.save()
        return price_t.price
    else:
        return price_t.price
