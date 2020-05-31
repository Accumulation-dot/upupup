import re

from django.contrib.auth import get_user_model, logout
from django.contrib.auth.backends import ModelBackend
from django.db.models import Count
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler, JSONWebTokenSerializer

from coins.models import query_award
from machine.models import machine_given_free
from tools.choices import award_sign_in
from tools.tools import CustomPagination
from user import models as um, serializers as us
from user.models import CoinUser, CoinUserInfo, user_info_creation, Identifier
from user.serializers import UserSerializer, CoinUserInfoSerializer, TeamSerializer

User = get_user_model()


class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = CoinUser.objects.get(username=username)
            if user.check_password(password):
                return user
        except Exception:
            return None


class UserCreation(generics.CreateAPIView):
    queryset = CoinUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            count = CoinUser.objects.aggregate(count=Count('id')).get('count', 0)
            if count is None and count <= 3000:
                user.level = 2
                user.save()
            user_info_creation(user)
            award_key = award_sign_in
            query_award(award_key, user=user)
            info = CoinUserInfo.objects.filter(user=user.id).first()
            info_serializer = CoinUserInfoSerializer(info)
            headers = self.get_success_headers(serializer.data)
            data = info_serializer.data

            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)

            data['token'] = token
            data['code'] = user.code
            return Response(data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception:
            return Response('用户已存在')


@api_view(['POST'])
@permission_classes([permissions.AllowAny, ])
def login_request(request, format=None):
    s = JSONWebTokenSerializer(data=request.data)
    try:
        s.is_valid(raise_exception=True)
        user = s.object.get('user')
    except (ValidationError, CoinUser.DoesNotExist):
        return Response('请输入正确的用户名和密码',)
    token = s.object.get('token')
    info = CoinUserInfo.objects.filter(user=user.id).first()
    response_data = CoinUserInfoSerializer(info).data
    response_data['token'] = token
    response_data['code'] = user.code
    return Response(response_data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated, ])
def identifier_request(request, format=None):
    user = request.user
    identifier = um.Identifier.objects.filter(user=user).first()
    if request.method == 'GET':
        if identifier is None:
            return Response('还没有进行验证', status=status.HTTP_204_NO_CONTENT)
        return Response(us.IdentifierSerializer(identifier).data, status=status.HTTP_200_OK)
    else:
        if identifier:
            return Response('已验证', )
        name = request.data.get('name', None)
        number = request.data.get('number', None)
        if name is None or number is None:
            return Response('请填写姓名和身份证号码')
        identifier_q = um.Identifier.objects.filter(number=number).first()
        if identifier_q is not None:
            return Response('当前身份证号码已被使用')
        ids = us.IdentifierSerializer(data=request.data)
        ids.is_valid(raise_exception=True)
        ids.save(user=user)
        machine_given_free(user=user)
        return Response(ids.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_summary(request, format=None):
    # 返回登陆名:手机号
    # 可用币
    # 购物币
    # 是否认证
    # 支付宝是否绑定
    # 银行卡是否绑定
    info = CoinUserInfo.objects.filter(user=request.user.id).first()
    return Response(us.SummarySerializer(info).data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_team(request, format=None):
    # 获取我的下面的人员
    infos = CoinUser.objects.filter(inviter=request.user.code).order_by('-date_joined')
    pagination = CustomPagination()
    query = pagination.paginate_queryset(infos, request)
    return pagination.get_paginated_response(TeamSerializer(query, many=True).data)


# 更改密码
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def user_forget_pd(request, format=None):
    # 获取身份证信息
    # 获取手机号码
    #
    un = request.data.get('un', '')
    ide = request.data.get('ide', '')
    np = request.data.get('np', "")
    if not un or not ide:
        return Response('请确保输入正确的信息,如果未绑定身份信息，请联系客服进行更改')
    try:
        user = CoinUser.objects.get(username=un)
        identifier = Identifier.objects.get(user=user, number=ide)
        reg = re.compile(r'^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{8,16}$')
        if reg.search(np) is None:
            return Response('密码必须是数字和字母的组合（8-16位）')
        user.set_password(np)
        user.save()
        return Response('密码更改成功，请使用新密码进行登陆', status=status.HTTP_202_ACCEPTED)
    except (CoinUserInfo.DoesNotExist, Identifier.DoesNotExist) as e:
        return Response('请确保输入正确的信息,如果未绑定身份信息，请联系客服进行更改')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def user_change_pd(request, format=None):
    old = request.data.get('op', '')
    np = request.data.get('np', "")
    if not old or not np:
        return Response('请输入原密码和新密码')
    if old == np:
        return Response('原密码与新密码一致')
    try:
        user = request.user
        if not user.check_password(old):
            # 密码错误
            return Response('请输入正确的原密码')
        reg = re.compile(r'^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{8,16}$')
        if reg.search(np) is None:
            return Response('密码必须是数字和字母的组合（8-16位）')
        user.set_password(np)
        user.save()
        if request.user:
            logout(request)
        return Response('密码更改成功，请使用新密码进行登陆', status=status.HTTP_202_ACCEPTED)
    except (CoinUserInfo.DoesNotExist, Identifier.DoesNotExist) as e:
        return Response('请确保输入正确的信息,如果未绑定身份信息，请联系客服进行更改')