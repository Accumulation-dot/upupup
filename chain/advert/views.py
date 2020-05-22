from rest_framework import generics, permissions as p, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from advert import models as am
from advert import serializers as ass
# Create your views here.
from coins.models import query_coin, query_rule
from coins import models as cm
from tools.tools import CustomPagination, identified
from tools import permissions as tp
from user.models import CoinUser


class ContentView(generics.ListAPIView):
    queryset = am.Content.objects.all()
    pagination_class = CustomPagination
    permission_classes = ([p.IsAuthenticated])
    serializer_class = ass.ContentSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CreationView(generics.CreateAPIView):
    queryset = am.Content.objects.all()
    pagination_class = CustomPagination
    permission_classes = ([p.IsAuthenticated])
    serializer_class = ass.ContentSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ContentDetailView(generics.RetrieveAPIView):
    queryset = am.Content.objects.all()
    permission_classes = ([p.IsAuthenticatedOrReadOnly])
    serializer_class = ass.ContentSerializer


class RecordView(generics.ListCreateAPIView):
    queryset = am.Record.objects.all()
    pagination_class = CustomPagination
    permission_classes = ([p.IsAuthenticatedOrReadOnly])
    serializer_class = ass.RecordSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RecordDetailView(generics.RetrieveAPIView):
    queryset = am.Record.objects.all()
    permission_classes = ([p.IsAuthenticatedOrReadOnly])
    serializer_class = ass.RecordSerializer


@api_view(['GET', ])
@permission_classes([p.IsAuthenticated, ])
def user_records(request, format=None):
    username = request.GET.get('username', request.user.username)
    # page = request.GET.get('page', '1')
    # size = request.GET.get('size', '30')
    user = CoinUser.objects.filter(username=username).first()
    if user and user.id:
        ads = am.Content.objects.filter(user=user)
        p = CustomPagination()
        query = p.paginate_queryset(ads, request)
        if query:
            return p.get_paginated_response(ass.ContentSummary(query, many=True).data)
        return p.get_paginated_response([])
    return Response(data='不存在的数据', status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([p.IsAuthenticated])
def advert_list(request, format=None):
    sells = am.Content.objects.all().exclude(user=request.user).order_by('-datetime')
    pagination = CustomPagination()
    query = pagination.paginate_queryset(sells, request)
    return pagination.get_paginated_response(ass.ContentSerializer(query, many=True).data)


class ContentOwnedView(generics.ListAPIView):
    queryset = am.Content.objects.all()
    pagination_class = CustomPagination
    permission_classes = (p.IsAuthenticated,)
    serializer_class = ass.ContentOwnedSerializer


@api_view(['GET'])
@permission_classes([p.IsAuthenticated])
def advert_mine(request, format=None):
    adverts = am.Content.objects.filter(user=request.user).order_by('-datetime')
    pagination = CustomPagination()
    query = pagination.paginate_queryset(adverts, request)
    return pagination.get_paginated_response(ass.ContentOwnedSerializer(query, many=True, context={'request': request}).data)


@api_view(['POST'])
@permission_classes([p.IsAuthenticated])
def advert_add(request, format=None):
    if not identified(user=request.user):
        return Response('你需要添加支付方式和进行个人信息认证')
    serializer = ass.ContentSerializer(data=request.data)
    coin = query_coin(request.user)
    rule = query_rule()
    if coin - rule.advert < 0:
        return Response('发布需要消耗{}币'.format(rule.advert))
    else:
        serializer.is_valid(raise_exception=True)
        cm.record_creation(request.user, key='advert', point=-rule.advert, desc='发布广告扣除')
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([p.IsAuthenticated])
def advert_up(request, format=None):
    coin = query_coin(request.user)
    rule = query_rule()
    if coin - rule.advert < 0:
        return Response('发布需要消耗{}币'.format(rule.advert))
    advert_id = request.data.get('advert')
    if not advert_id:
        return Response('请选择需要置顶的广告')
    try:
        advert = am.Content.objects.get(pk=advert_id)
        cm.record_creation(request.user, key='advert', point=-rule.advert, desc='置顶广告扣除')
        advert.save()
        return Response('置顶成功', status=status.HTTP_202_ACCEPTED)
    except am.Content.DoesNotExist:
        return Response('请选择需要置顶的广告')
