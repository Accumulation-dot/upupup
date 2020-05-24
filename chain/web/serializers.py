from rest_framework import serializers

from web.models import AppVersion


class AppVersionS(serializers.ModelSerializer):

    flag = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = AppVersion
        fields = ('version', 'flag', 'app',)

    def get_flag(self, obj):
        if obj.flag:
            return 1
        else:
            return 0
