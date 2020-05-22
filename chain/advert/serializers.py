from rest_framework import serializers as rfs

from advert import models
from user.serializers import user_info_data, user_name


class ContentSerializer(rfs.ModelSerializer):

    user = rfs.SerializerMethodField(read_only=True)

    username = rfs.SerializerMethodField(read_only=True)

    datetime = rfs.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    class Meta:
        model = models.Content
        exclude = ('readers',)

    def get_user(self, objc):
        return user_name(objc.user)
        # user_info_data(objc.user)

    def get_username(self, objc):
        return user_name(objc.user)


class ContentOwnedSerializer(rfs.ModelSerializer):

    user = rfs.SerializerMethodField(read_only=True)

    username = rfs.SerializerMethodField(read_only=True)

    datetime = rfs.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    img = rfs.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Content
        exclude = ('readers',)

    def get_user(self, objc):
        return user_name(objc.user)
        # user_info_data(objc.user)

    def get_username(self, objc):
        return user_name(objc.user)

    def get_img(self, obj):
        request = self.context.get('request')
        img_url = obj.img.url
        return request.build_absolute_uri(img_url)


class ContentSummary(rfs.ModelSerializer):

    class Meta:
        model = models.Content
        exclude = ('readers', 'user', )


class RecordSerializer(rfs.ModelSerializer):
    user = rfs.SerializerMethodField(read_only=True)

    contents = rfs.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Record
        fields = '__all__'

    def get_user(self, objc):
        return user_info_data(objc.user)

    def get_contents(self, objc):
        return ContentSerializer(models.Content.objects.filter(id=objc.content.id).first()).data

