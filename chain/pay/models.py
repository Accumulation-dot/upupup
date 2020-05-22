from django.db import models
from django.db.models import Count, Q

from tools.base import BaseModel
from tools.choices import pay_choices
from user import models as um


class Pay(BaseModel):
    """
    支付信息
    """
    user = models.ForeignKey(um.CoinUser, on_delete=models.DO_NOTHING)
    type = models.CharField(max_length=20, choices=pay_choices)
    name = models.CharField(max_length=10)
    number = models.CharField(max_length=30)
    use = models.BooleanField(default=True, verbose_name='use_state', help_text='是否在使用')

    class Meta:
        verbose_name = verbose_name_plural = '支付信息'
        unique_together = ('number', 'type',)
        # unique_together = ('type', 'name', 'number', 'user')


# def payment_count(user):
#     r = Pay.objects.aggregate(count=Count('id', filter=Q(use=True) & Q(user=user)))
#     return r.get('count', 0)


def payment_count(user, t=None):
    if t is None:
        r = Pay.objects.aggregate(count=Count('id', filter=Q(use=True) & Q(user=user)))
    else:
        r = Pay.objects.aggregate(count=Count('id', filter=Q(use=True) & Q(user=user) & Q(type=t)))
    return r.get('count', 0)


def payment_exist(t, number):
    r = Pay.objects.filter(number=number, type=t).first()
    return r is not None
