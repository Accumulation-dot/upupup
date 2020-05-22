from rest_framework import serializers as rfs

from coins import models as csm


class RecordSerializer(rfs.ModelSerializer):

    datetime = rfs.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    class Meta:
        model = csm.Record
        exclude = ('user', 'id',)


class AwardSerializer(rfs.ModelSerializer):

    class Meta:
        model = csm.Award
        fields = '__all__'


class RuleSerializer(rfs.ModelSerializer):

    class Meta:
        model = csm.CoinRule
        exclude = ('used', 'id', 'pay')
