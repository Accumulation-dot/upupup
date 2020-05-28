from rest_framework.serializers import ModelSerializer, SerializerMethodField, DateTimeField

from coins.models import query_coin, query_shop
from user import models
from user.models import CoinUser, CoinUserInfo
from pay.models import payment_count


class UserSerializer(ModelSerializer):
    def create(self, validated_data):
        user = CoinUser.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            inviter=validated_data['inviter'],
        )
        return user

    class Meta:
        model = CoinUser
        exclude = ('level',)


class UserRegisterSerializer(ModelSerializer):
    class Meta:
        model = CoinUser
        fields = ('username', 'password',)


class CoinUserInfoSerializer(ModelSerializer):
    coin = SerializerMethodField(read_only=True)

    created = DateTimeField(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = CoinUserInfo
        exclude = ('id', 'user', 'name',)

    def get_coin(self, objc):
        return query_coin(objc.user)


class SummarySerializer(ModelSerializer):

    identified = SerializerMethodField(read_only=True)

    bank = SerializerMethodField(read_only=True)

    ali = SerializerMethodField(read_only=True)

    count = SerializerMethodField(read_only=True)

    shop = SerializerMethodField(read_only=True)

    phone = SerializerMethodField(read_only=True)

    created = DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    class Meta:
        model = CoinUserInfo
        exclude = ('user',)

    # 0 未验证 1 已验证
    def get_identified(self, obj):
        identifier = models.Identifier.objects.filter(user=obj.user).first()
        if identifier is None:
            return 0
        return 1

    # 0 未填写
    def get_bank(self, obj):
        bank = payment_count(user=obj.user, t='BANK')
        return bank

    def get_ali(self, obj):
        ali = payment_count(user=obj.user, t='ALI')
        return ali

    def get_count(self, obj):
        return query_coin(user=obj.user)

    def get_shop(self, obj):
        return query_shop(user=obj.user)

    def get_phone(self, obj):
        return obj.user.username


class IdentifierSerializer(ModelSerializer):
    class Meta:
        model = models.Identifier
        exclude = ('id', 'user',)


def user_info_data(user):
    return CoinUserInfoSerializer(CoinUserInfo.objects.filter(user=user).first()).data


def user_info_address(user):
    try:
        coinUserInfo = CoinUserInfo.objects.get(user=user)
    except CoinUserInfo.DoesNotExist as e:
        return ''
    return coinUserInfo.address


def user_name(user):
    return user.username


class TeamSerializer(ModelSerializer):

    date_joined = DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    # #SerializerMethodField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    class Meta:
        model = CoinUser
        fields = ('username', 'date_joined',)
