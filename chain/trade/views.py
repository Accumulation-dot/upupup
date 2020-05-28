import datetime

from django.db.models import Count, Q
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from coins import models as csm
from tools.permissions import UnOwned, Owned
from tools.tools import CustomPagination, identified
from trade import models as tm, serializers as tss


# 获取别人的出售订单
@api_view(['GET'])
@permission_classes([UnOwned, IsAuthenticated])
def sell_list(request, format=None):
    t_price = tm.today_price() * 0.97
    sells = tm.Sell.objects.filter(status=0, price__gte=t_price).exclude(user=request.user).order_by('-price', '-created')
    pagination = CustomPagination()
    query = pagination.paginate_queryset(sells, request)
    return pagination.get_paginated_response(tss.SellSummarySerializer(query, many=True).data)


# 获取自己的订单 出售
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sell_mine(request, format=None):
    status = request.GET.get('status')
    if status is not None:
        sells = tm.Sell.objects.filter(status=status, user=request.user).order_by('-created')
    else:
        sells = tm.Sell.objects.filter(user=request.user).order_by('-created')
    pagination = CustomPagination()
    query = pagination.paginate_queryset(sells, request)
    return pagination.get_paginated_response(tss.SellMineSerializer(query, many=True).data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sell_cancel(request, format=None):
    serial_no = request.data.get('s_no')
    if not serial_no:
        return Response('需要提供订单号')
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    sell = tm.Sell.objects.filter(serial_no=serial_no, created__lt=yesterday).first()
    if not sell:
        return Response('订单需要持续24小时才能被取消')
    sell_record = tm.SellRecord.objects.filter(sell=sell, status__range=(0, 2)).first()
    if sell_record is not None:
        return Response('当前订单已被预定，不能进行取消')

    result = tm.Sell.objects.filter(serial_no=serial_no, status=0).update(status=4)
    if result == 0:
        return Response('请刷新数据重试，当前订单可能已被预定')
    rule = csm.query_rule()
    shop = min(1.0, max(0.0, rule.shop))
    cash = int(sell.number) * int((1.0 + min(1.0, max(0.0, rule.tax)) + shop) * 100) / 100
    csm.record_creation(user=request.user, key='sell back', point=float(cash), desc='出售取消')
    return Response(tss.SellMineSerializer(tm.Sell.objects.filter(serial_no=serial_no).first()).data,
                    status=status.HTTP_202_ACCEPTED)


# 发布自己的出售订单
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sell_item(request, format=None):
    if not identified(user=request.user):
        return Response('你需要添加支付方式和进行个人信息认证才能进行交易')

    query = tm.Sell.objects.aggregate(count=Count('id', filter=Q(status=0) & Q(user=request.user))).get('count', 0)
    if query >= 3:
        return Response('发布的订单只能有3个为可预定状态')

    number = request.data.get('number')
    price = request.data.get('price')
    if not number:
        return Response('必须填写数量才能进行发布')
    if not price:
        return Response('你必须填写单价')
    serializer = tss.SellSummarySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    coin = csm.query_coin(request.user)
    rule = csm.query_rule()
    shop = min(1.0, max(0.0, rule.shop))
    cash = int(number) * int((1.0 + min(1.0, max(0.0, rule.tax)) + shop) * 100) / 100
    # cash = float(number) * 1.5
    # (1.0 + min(1.0, max(0.0, rule.tax)))
    if cash > coin - rule.min_num:
        return Response(data='你当前的SD不足， 请保证售卖之后还能保留最少{}个SD'.format(str(rule.min_num)), status=status.HTTP_200_OK)
    serializer.save(user=request.user)
    # cr(user=request.user, key='selling', point=float(cash) * -1, desc='挂单出售').save()
    try:

        csm.record_creation(user=request.user, key='selling', point=float(cash) * -1, desc='挂单出售')
    except ValueError as e:
        print(e)
    finally:
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# 预定订单
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sell_order(request, format=None):
    if not identified(user=request.user):
        return Response('你需要添加支付方式和进行个人信息认证才能进行交易')
    serial_no = request.data.get('s_no')
    if not serial_no:
        return Response('需要提供订单号')
    try:
        sell = tm.Sell.objects.get(serial_no=serial_no)
    except tm.Sell.DoesNotExist:
        return Response('不存在的订单')
    if sell.user == request.user:
        return Response('请选择其他的订单, 你不能预定自己发布的订单')
    if sell.status != 0:
        return Response('当前订单已被预定')
    data = {'sell': sell.id}
    serializer = tss.SellRecordSerializer(data=data)
    try:
        serializer.is_valid(raise_exception=True)
        result = tm.Sell.objects.filter(serial_no=serial_no, status=0).update(status=1)
        if result == 0:
            return Response('请刷新重试')
        # sell = tm.Sell.objects.get(serial_no=serial_no)
        serializer.save(user=request.user)
    except ValidationError as ve:
        return Response('请填写正确的内容{}'.format(ve))
    else:
        # return Response(tss.SellSerializer(sell).data,
        #                 status=status.HTTP_201_CREATED)
        return Response(tss.SellRecordInfoSerializer(serializer.instance).data,
                        status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sell_order_mine(request, format=None):
    status = request.GET.get('status')
    if status is not None:
        sell_orders = tm.SellRecord.objects.filter(status=status, user=request.user)
    else:
        sell_orders = tm.SellRecord.objects.filter(user=request.user)
    pagination = CustomPagination()
    query = pagination.paginate_queryset(sell_orders, request)
    # query = map(lambda x: x.sell, query)
    return pagination.get_paginated_response(tss.SellRecordInfoSerializer(query, many=True).data)
    # tss.SellRecordInfoSerializer(query, many=True).data)


# 填写付款信息 s_no 订单号 ali 支付订单号 预定订单信息
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sell_order_fill(request, format=None):
    serial_no = request.data.get('s_no')
    ali = request.data.get('order')
    if serial_no is None or ali is None:
        return Response('请输入完整的信息：订单编号和支付订单号码')
    try:
        record = tm.SellRecord.objects.get(serial_no=serial_no, user=request.user, status=0)
    except tm.SellRecord.DoesNotExist:
        return Response('不存在的订单或订单已被预定')
    else:
        detail = tm.SellDetail.objects.aggregate(count=Count('id', filter=Q(record=record.id))).get('count', 0) > 0
        if detail:
            return Response('你已经添加')
        serializer = tss.SellDetailSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            result = tm.SellRecord.objects.filter(serial_no=serial_no, user=request.user, status=0).update(status=1)
            result2 = tm.Sell.objects.filter(id=record.sell.id, status=1).update(status=2)
            if result == 0 or result2 == 0:
                return Response('更新失败，请刷新后重试')
            serializer.save(record=record)
            record = tm.SellRecord.objects.get(pk=record.pk)
        except ValidationError as e:
            return Response('数据错误')
        else:
            return Response(tss.SellRecordInfoSerializer(record).data,
                            status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sell_detail(request, serial, format=None):
    return Response()


# 确定订单， 订单号码为原始订单号码
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def sell_confirm(request, format=None):
    serial_no = request.data.get('s_no')
    try:
        sell = tm.Sell.objects.get(serial_no=serial_no, status=2)
    except tm.Sell.DoesNotExist:
        return Response('当前订单不存在，请刷新重试')
    result = tm.Sell.objects.filter(serial_no=serial_no, status=2).update(status=3)
    result2 = tm.SellRecord.objects.filter(sell=sell, status=1).update(status=2)
    if result == 0 or result2 == 0:
        return Response('订单确认发生错误， 请刷新重试')
    try:
        sell = tm.Sell.objects.get(serial_no=serial_no)
        record = tm.SellRecord.objects.get(sell=sell)
        rule = csm.query_rule()
        shop = min(1.0, max(0.0, rule.shop))
        csm.record_creation(user=record.user, point=sell.number, key='buy from others', desc='购买')
        if shop > 0:
            csm.record_creation(user=sell.user, point=0, key='shop', shop=int(sell.number * shop * 100) / 100, desc='出售获取')
        tm.trade_creation(sell.price, sell.number)
    except tm.Sell.DoesNotExist or tm.SellRecord.DoesNotExist or ValueError:
        return Response('获取订单不存在，请刷新重试')

    return Response(tss.SellSerializer(sell).data, status=status.HTTP_202_ACCEPTED)

    # return Response('确认成功')


@api_view(['POST', ])
@permission_classes([IsAuthenticated])
def buy_item(request, format=None):
    # if request.method == 'POST':
    if not identified(user=request.user):
        return Response('你需要添加支付方式和进行个人信息认证才能进行交易')

    number = request.data.get('number')
    price = request.data.get('price')
    if not number or not price:
        return Response('必须填写订单数量和单价')
    query = tm.Buy.objects.aggregate(count=Count('id', filter=Q(status=0) & Q(user=request.user))).get('count', 0)
    if query >= 3:
        return Response('发布的订单只能有3个为可预定状态')

    trade = tss.BuySerializer(data=request.data)
    trade.is_valid(raise_exception=True)
    trade.save(user=request.user)
    return Response(trade.data, status=status.HTTP_201_CREATED)


@api_view(['POST', ])
@permission_classes([IsAuthenticated])
def buy_cancel(request, format=None):
    serial_no = request.data.get('s_no')
    if not serial_no:
        return Response('需要提供订单号')
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    buy = tm.Buy.objects.filter(serial_no=serial_no, created__lt=yesterday).first()
    if not buy:
        return Response('订单需要持续24小时才能被取消')
    buy_record = tm.BuyRecord.objects.filter(buy=buy, status__range=(0, 2)).first()
    if buy_record is not None:
        return Response('当前订单已被预定，不能进行取消')

    result = tm.Sell.objects.filter(serial_no=serial_no, status=0).update(status=4)
    if result == 0:
        return Response('请刷新数据重试，当前订单可能已被预定')

    return Response(tss.SellMineSerializer(tm.Sell.objects.filter(serial_no=serial_no).first()).data,
                    status=status.HTTP_202_ACCEPTED)



# 收购API
@api_view(['GET', ])
@permission_classes([UnOwned])
def buy_list(request, format=None):
    t_price = tm.today_price() * 0.97
    buys = tm.Buy.objects.filter(status=0, price__gte=t_price).exclude(user=request.user).order_by('-price', '-created')
    pagination = CustomPagination()
    query = pagination.paginate_queryset(buys, request)
    return pagination.get_paginated_response(tss.BuySummarySer(query, many=True).data)


# 我的收购API
@api_view(['GET', ])
@permission_classes([IsAuthenticated])
def buy_mine(request, format=None):
    status = request.GET.get('status')
    if status is not None:
        buys = tm.Buy.objects.filter(status=status, user=request.user).order_by('-created')
    else:
        buys = tm.Buy.objects.filter(user=request.user).order_by('-created')
    pagination = CustomPagination()
    query = pagination.paginate_queryset(buys, request)
    return pagination.get_paginated_response(tss.BuySerializer(query, many=True).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def buy_fill(request, format=None):
    serial_no = request.data.get('s_no')
    order = request.data.get('order')
    img = request.data.get('img')
    if serial_no is None or img is None:
        return Response('请输入要支付的订单号')
    try:
        record = tm.BuyRecord.objects.get(serial_no=serial_no, status=0)
    except tm.BuyRecord.DoesNotExist as e:
        return Response('请刷新后重试')

    result = tm.BuyRecord.objects.filter(serial_no=serial_no, status=0).update(status=1)

    result2 = tm.Buy.objects.filter(status=1, pk=record.buy.id).update(status=2)

    if result == 0 or result2 == 0:
        return Response('更新发生错误 请联系管理员')
    serializer = tss.BuyDetailSerializer(data=request.data)
    try:
        serializer.is_valid(raise_exception=True)
        serializer.save(record=record)
        buy = tm.Buy.objects.get(pk=record.buy.id)
    except ValidationError and tm.Buy.DoesNotExist:
        return Response('请联系管理员 刷新数据')
    return Response(tss.BuySerializer(buy).data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def buy_order(request, format=None):
    if not identified(user=request.user):
        return Response('你需要添加支付方式和进行个人信息认证才能进行交易')
    serial_no = request.data.get('s_no')
    if serial_no is None:
        return Response('需要提供订单号')

    try:
        buy = tm.Buy.objects.get(serial_no=serial_no, status=0)
    except tm.Buy.DoesNotExist as ne:
        return Response('当前订单不存在或已经被预定')

    if buy.user == request.user:
        return Response('请选择其他不属于你的订单')
    coin = csm.query_coin(request.user)
    rule = csm.query_rule()
    shop = min(1.0, max(0.0, rule.shop))
    cash = int(buy.number) * int((1.0 + min(1.0, max(0.0, rule.tax)) + shop) * 100) / 100
    if cash > coin - rule.min_num:
        return Response('请保证你支付之后的余额大与{}'.format(rule.min_num),)
    data = {'buy': buy.id, 'user': request.user.id}
    serializer = tss.BuyRecordSaveSerial(data=data)
    serializer.is_valid(raise_exception=True)
    result = tm.Buy.objects.filter(serial_no=serial_no, status=0).update(status=1)
    if result == 0:
        return Response('请刷新重试')
    record = serializer.save()
    try:
        csm.record_creation(user=request.user, key='sell', point=float(cash) * -1, desc='出售给其他人')
        if shop > 0:
            csm.record_creation(user=request.user, key='shop', point=0, shop=buy.number * shop, desc='出售获取')
    except ValueError as e:
        print(e)
        return Response('如果出现问题，请联系管理员')
        # return Response(BuyRecordInfoSerializer(buy_re).data, status=status.HTTP_201_CREATED)
    return Response(tss.BuyRecordInfoSerializer(tm.BuyRecord.objects.filter(pk=record.pk).first()).data, status=status.HTTP_201_CREATED)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def buy_order_mine(request, format=None):
    request_s = request.GET.get('status')
    if request_s is not None:
        records = tm.BuyRecord.objects.filter(status=request_s, user=request.user).order_by('-created')
    else:
        records = tm.BuyRecord.objects.filter(user=request.user).order_by('-created')
    pagination = CustomPagination()
    query = pagination.paginate_queryset(records, request)
    return pagination.get_paginated_response(tss.BuyRecordInfoSerializer(query, many=True).data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def buy_order_confirm(request, format=None):
    serial_no = request.data.get('s_no')
    if serial_no is None:
        return Response('请输入订单号',)
    try:
        record = tm.BuyRecord.objects.get(serial_no=serial_no, status=1)
    except tm.BuyRecord.DoesNotExist as e:
        return Response('状态已更新，请刷新并重试')
    result = tm.Buy.objects.filter(pk=record.buy_id, status=2).update(status=3)
    result2 = tm.BuyRecord.objects.filter(serial_no=serial_no, status=1).update(status=2)
    if result == 0 or result2 == 0:
        return Response('提交错误，请刷新重试！')
    try:
        csm.record_creation(user=record.buy.user, point=record.buy.number, desc='挂单购买成功', key='buy')
        tm.trade_creation(price=record.buy.price, count=record.buy.number)
    except ValueError as e:
        print(e)
    finally:
        record = tm.BuyRecord.objects.filter(pk=record.pk, status=2).first()
        return Response(tss.BuyRecordInfoSerializer(record).data,
                        status=status.HTTP_202_ACCEPTED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def price(request, format=None):
    return Response(tm.today_price())
