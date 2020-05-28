from rest_framework import serializers as rfs

from pay.serializers import pay_for_user
from trade import models as tm
from user.serializers import user_info_address

# 主动收 主动卖
#

# 出售


class SellSerializer(rfs.ModelSerializer):
    user = rfs.SerializerMethodField(read_only=True)

    status_desc = rfs.CharField(source='get_status_display', read_only=True)

    created = rfs.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    pays = rfs.SerializerMethodField(read_only=True)

    class Meta:
        model = tm.Sell
        exclude = ('id',)

    def get_user(self, obj):
        # return user_info_data(obj.user)
        return obj.user.username
        # user_info_address(obj.user)

    def get_pays(self, obj):
        return pay_for_user(obj.user)


class SellSummarySerializer(rfs.ModelSerializer):
    user = rfs.SerializerMethodField(read_only=True)

    status_desc = rfs.CharField(source='get_status_display', read_only=True)

    created = rfs.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    class Meta:
        model = tm.Sell
        exclude = ('id',)

    def get_user(self, obj):
        return user_info_address(obj.user)


class SellRecordSerializer(rfs.ModelSerializer):
    user = rfs.SerializerMethodField(read_only=True)

    created = rfs.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    class Meta:
        model = tm.SellRecord
        exclude = ('id',)

    def get_user(self, obj):
        # return user_info_data(obj.user)
        return user_info_address(obj.user)


class SellRecordInfoSerializer(rfs.ModelSerializer):
    user = rfs.SerializerMethodField(read_only=True)

    created = rfs.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    sell = rfs.SerializerMethodField(read_only=True)

    status_desc = rfs.CharField(source='get_status_display', read_only=True)

    detail = rfs.SerializerMethodField(read_only=True)

    class Meta:
        model = tm.SellRecord
        exclude = ('id',)

    def get_user(self, obj):
        return obj.user.username
        # user_info_address(obj.user)

    def get_sell(self, obj):
        return SellSerializer(obj.sell).data

    def get_detail(self, obj):
        try:
            detail = tm.SellDetail.objects.get(record=obj.id)
        except tm.SellDetail.DoesNotExist as e:
            return ''
        return detail.img.url


class SellMineSerializer(rfs.ModelSerializer):
    user = rfs.SerializerMethodField(read_only=True)

    status_desc = rfs.CharField(source='get_status_display', read_only=True)

    created = rfs.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    pays = rfs.SerializerMethodField(read_only=True)

    detail = rfs.SerializerMethodField(read_only=True)

    class Meta:
        model = tm.Sell
        exclude = ('id',)

    def get_user(self, obj):
        # return user_info_data(obj.user)
        return obj.user.username
        # user_info_address(obj.user)

    def get_pays(self, obj):
        return pay_for_user(obj.user)

    def get_detail(self, obj):
        try:
            record = tm.SellRecord.objects.get(sell=obj.id, status=1)
            detail = tm.SellDetail.objects.get(record=record)
            return detail.img.url
        except:
            return ''


class SellDetailSerializer(rfs.ModelSerializer):
    record = rfs.SerializerMethodField(read_only=True)

    created = rfs.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    class Meta:
        model = tm.SellDetail
        fields = '__all__'

    def get_record(self, obj):
        try:
            sell = tm.Sell.objects.get(pk=obj.record.id)
            return SellSerializer(sell).data
        except tm.Sell.DoesNotExist as e:
            return SellSerializer(None).data


class BuyDetailSerializer(rfs.ModelSerializer):
    record = rfs.SerializerMethodField(read_only=True)

    created = rfs.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    class Meta:
        model = tm.BuyDetail
        fields = '__all__'

    def get_record(self, obj):
        return BuySerializer(tm.Buy.objects.filter(pk=obj.record.id).first()).data


# buy_mine/ buy / record
class BuyRecordSerializer(rfs.ModelSerializer):
    user = rfs.SerializerMethodField(read_only=True)
    # buy = rfs.SerializerMethodField(read_only=True)
    #
    # detail = rfs.SerializerMethodField(read_only=True)
    pays = rfs.SerializerMethodField(read_only=True)

    status_desc = rfs.CharField(source='get_status_display', read_only=True)

    created = rfs.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    detail = rfs.SerializerMethodField(read_only=True)

    class Meta:
        model = tm.BuyRecord
        exclude = ('id', 'buy',)

    def get_user(self, obj):
        return obj.user.username

    def get_pays(self, obj):
        return pay_for_user(obj.user)

    def get_detail(self, obj):
        try:
            detail = tm.BuyDetail.objects.get(record=obj.id)
            print(detail)
            return detail.img.url #
            # BuyDetailSerializer(detail).data
        except tm.BuyDetail.DoesNotExist:
            return ''


# buy_mine / buy /
class BuySerializer(rfs.ModelSerializer):
    user = rfs.SerializerMethodField(read_only=True)

    created = rfs.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    status_desc = rfs.ReadOnlyField(source='get_status_display')

    records = rfs.SerializerMethodField(read_only=True)

    class Meta:
        model = tm.Buy
        exclude = ('id',)

    def get_user(self, obj):
        return user_info_address(obj.user)
        # user_info_data(obj.user)

    def get_records(self, obj):
        if obj.status == 0:
            return {}
        return BuyRecordSerializer(tm.BuyRecord.objects.filter(buy=obj.id, status=obj.status - 1).first()).data


# buy_list
class BuySummarySer(rfs.ModelSerializer):
    user = rfs.SerializerMethodField(read_only=True)

    created = rfs.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    status_desc = rfs.ReadOnlyField(source='get_status_display')

    class Meta:
        model = tm.Buy
        exclude = ('id',)

    def get_user(self, obj):
        return user_info_address(obj.user)


# 预定订单内显示
class BuySummary(rfs.ModelSerializer):
    user = rfs.SerializerMethodField(read_only=True)

    created = rfs.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    status_desc = rfs.ReadOnlyField(source='get_status_display')

    class Meta:
        model = tm.Buy
        exclude = ('id',)

    def get_user(self, obj):
        return obj.user.username


# 我的订单 ： 别人显示
class BuyRecordInfoSerializer(rfs.ModelSerializer):
    # user = rfs.SerializerMethodField(read_only=True)

    created = rfs.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    status_desc = rfs.ReadOnlyField(source='get_status_display')

    buy = rfs.SerializerMethodField(read_only=True)

    pays = rfs.SerializerMethodField(read_only=True)

    detail = rfs.SerializerMethodField(read_only=True)

    class Meta:
        model = tm.BuyRecord
        exclude = ('id', 'user',)

    def get_user(self, obj):
        return obj.user.username

    def get_buy(self, obj):
        return BuySummary(obj.buy).data

    def get_pays(self, obj):
        return pay_for_user(obj.user)

    def get_detail(self, obj):
        try:
            detail = tm.BuyDetail.objects.get(record=obj.id)
            return detail.img.url
        except tm.BuyDetail.DoesNotExist:
            return ''


class BuyInformationSerializer(rfs.ModelSerializer):
    seller = rfs.SerializerMethodField(read_only=True)

    class Meta:
        model = tm.Buy
        exclude = ('id',)

    def get_seller(self, objc):
        record = tm.BuyRecord.objects.filter(buy=objc, status__in=(0, 1, 3))
        return BuyRecordSerializer(record, many=True).data


class TradeSerializer(rfs.ModelSerializer):
    class Meta:
        model = tm.Trade
        fields = '__all__'


class BuyRecordSaveSerial(rfs.ModelSerializer):
    class Meta:
        model = tm.BuyRecord
        fields = '__all__'

