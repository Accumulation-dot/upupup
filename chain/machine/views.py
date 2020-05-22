from datetime import datetime, timedelta

from django.db.models import Count, Q
from rest_framework import generics, status
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from django.db import transaction

from coins import models as cm
from machine import models
from machine import serializers
from tools.permissions import Owned
from tools.tools import CustomPagination


# Create your views here.
from user.models import inviter_query


class MachineView(generics.ListAPIView):
    pagination_class = CustomPagination
    queryset = models.Machine.objects.all()
    permission_classes = ([permissions.IsAuthenticatedOrReadOnly])
    serializer_class = serializers.MachineSerializer


class RecordView(generics.ListCreateAPIView):
    pagination_class = CustomPagination
    queryset = models.Machine.objects.all()
    permission_classes = ([permissions.IsAuthenticatedOrReadOnly, ])
    serializer_class = serializers.RecordSerializer


class RecordInfoView(generics.RetrieveUpdateAPIView):
    queryset = models.Record.objects.all()
    serializer_class = serializers.RecordUpdateSerializer
    permission_classes = ([permissions.IsAuthenticated, Owned])


@api_view(['GET'])
@permission_classes([Owned])
def mine(request, format=None):
    t = datetime.now()
    print(request.GET)
    # 1 可用 2 已过期 0全部

    s = int(request.GET.get('status', 0))
    print(s)
    if s == 0:
        records = models.Record.objects.filter(user=request.user).order_by('-expired')
    elif s == 2:
        records = models.Record.objects.filter(expired__lt=t, user=request.user).order_by('-expired')
    else:
        records = models.Record.objects.filter(expired__gt=t, user=request.user).order_by('-expired')
    # records = models.Record.objects.all()
    pagination = CustomPagination()
    query = pagination.paginate_queryset(records, request)
    return pagination.get_paginated_response(serializers.RecordSerializer(query, many=True).data)


@api_view(['POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def order(request, format=None):
    serial_no = request.data.get('s_no')
    if serial_no is None:
        return Response('请输入正确的内容')
    try:
        machine = models.Machine.objects.get(s_no=serial_no)
    except models.Machine.DoesNotExist as e:
        return Response('不存在的矿机号码')

    if machine.given:
        return Response('体验项不能二次购买')

    now = datetime.now()

    coin = cm.query_coin(request.user)

    if coin < machine.cost:
        return Response('当前币不足，不足以支付')

    all_count = models.Record.objects.aggregate(count=Count('id', filter=Q(machine=machine.id) & Q(user=request.user)))
    days = machine.days + machine.append * all_count.get('count', 0)
    with transaction.atomic():
        sid = transaction.savepoint()
        try:
            r = models.Record(user=request.user, machine=machine, expired=now + timedelta(days=days),
                              number=float('%.03f' % (int(machine.number * 1000 / days) / 1000.0)), days=days)
            r.save()
            cm.record_creation(user=request.user, point=machine.cost * -1, key='rent machine', desc='购买矿机')

            inviter = inviter_query(request.user)
            if inviter is not None:
                cm.record_creation(user=inviter, point=machine.cost * 0.05, key='award from other', desc='奖励：团员购买节点')
            return Response(serializers.RecordSerializer(r).data, status=status.HTTP_201_CREATED)
        except Exception:
            transaction.rollback(sid)
            return Response('请刷新重试，如果还是有问题 请联系管理员')


@api_view(['GET'])
@permission_classes([Owned])
def machine_task_all(request, format=None):
    return Response(models.machine_earn_count(request.user))


@api_view(['GET'])
@permission_classes([AllowAny])
def customer_service(request, format=None):
    return Response(serializers.CSSerailizer(models.CustomerService.objects.all().first()).data)
