from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from pay import models as pm, serializers as ps
# Create your views here.
from tools.permissions import Owned
from tools.tools import CustomPagination


@api_view(['GET', 'POST'])
@permission_classes([Owned])
def pay(request, format=None):
    if request.method == "GET":
        r = pm.Pay.objects.filter(user=request.user)[:2]
        pagination = CustomPagination()
        query = pagination.paginate_queryset(r, request)
        return pagination.get_paginated_response(ps.PaySerializer(query, many=True).data, )
    else:
        if pm.payment_count(request.user) >= 2:
            return Response('你当前已经有2条记录了')
        serializer = ps.PaySerializer(data=request.data)
        # 查询是否已经被使用
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
        except ValidationError as e:
            return Response(serializer.errors, )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', "POST"])
@permission_classes([IsAuthenticated])
def bank(request, format=None):
    bank_t = 'BANK'
    if request.method == 'GET':
        bank_r = pm.Pay.objects.filter(user=request.user, type=bank_t)
        pagination = CustomPagination()
        query = pagination.paginate_queryset(bank_r, request)
        return pagination.get_paginated_response(ps.PaySerializer(query, many=True).data, )
    else:
        bank_no = request.data.get('number')
        if bank_no is None:
            return Response('请输入银行卡号')
        if pm.payment_count(request.user, bank_t) > 0:
            return Response('银行卡已添加')
        if pm.payment_exist(bank_t, bank_no):
            return Response('当前银行卡已被添加')
        serializer = ps.PaySerializer(data={'number': bank_no, 'type': bank_t, 'name': '银行卡'})
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response('请输入正确的号码')


@api_view(['GET', "POST"])
@permission_classes([IsAuthenticated])
def ali_pay(request, format=None):
    alipay = 'ALI'
    if request.method == 'GET':
        bank_r = pm.Pay.objects.filter(user=request.user, type=alipay)
        pagination = CustomPagination()
        query = pagination.paginate_queryset(bank_r, request)
        return pagination.get_paginated_response(ps.PaySerializer(query, many=True).data, )
    else:
        ali_no = request.data.get('number')
        if ali_no is None:
            return Response('请输入银行卡号')
        if pm.payment_count(request.user, alipay) > 0:
            return Response('银行卡已添加')
        if pm.payment_exist(alipay, ali_no):
            return Response('当前支付宝已被添加')
        serializer = ps.PaySerializer(data={'number': ali_no, 'type': alipay, 'name': '支付宝'})
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response('请输入正确的号码')


@api_view(['PATCH', 'GET', ])
@permission_classes([IsAuthenticated])
def pay_update(request, pk, format=None):
    try:
        r = pm.Pay.objects.get(pk=pk)
        if request.method == 'PATCH':
            if request.user != r.user:
                return Response('没有权限', status=status.HTTP_403_FORBIDDEN, )
            serializer = ps.PaySerializer(r, data=request.data, partial=True, )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, )
        else:
            serializer = ps.PaySerializer(r)
            return Response(serializer.data)
    except pm.Pay.DoesNotExist:
        return Response('不存在的节点', status=status.HTTP_404_NOT_FOUND)
    except ValidationError:
        return Response("提交数据有问题", status=status.HTTP_400_BAD_REQUEST)
