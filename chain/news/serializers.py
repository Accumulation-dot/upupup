from rest_framework import serializers as rfs

from news import models as nsm
from user.serializers import user_info_address


# class ContentSerializer(rfs.ModelSerializer):
#     datetime = rfs.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
#
#     class Meta:
#         model = nsm.Content
#         # fields = '__all__'
#         exclude = ('readers',)
#
#
# def news_content(news):
#     try:
#         content = nsm.Content.objects.get(pk=news.id)
#         return ContentSerializer(content).data
#     except nsm.Content.DoesNotExist as e:
#         return None
#
#
# class RecordSerializer(rfs.ModelSerializer):
#
#     class Meta:
#         model = nsm.Record
#         exclude = ('user', 'address',)
#
#
# class RecordDetailSerializer(rfs.ModelSerializer):
#     user = rfs.SerializerMethodField(read_only=True)
#
#     news = rfs.SerializerMethodField(read_only=True)
#
#     class Meta:
#         model = nsm.Record
#         fields = '__all__'
#
#     def get_user(self, obj):
#         return user_info_data(obj.user)
#
#     def get_news(self, obj):
#         return news_content(obj.news)


class NewsSerializer(rfs.ModelSerializer):
    date = rfs.DateField(format='%Y-%m-%d', read_only=True)

    class Meta:
        model = nsm.News
        exclude = ('created',)


class TaskSerializer(rfs.ModelSerializer):
    user = rfs.SerializerMethodField(read_only=True)

    class Meta:
        model = nsm.Task
        exclude = ('id', )

    def get_user(self, obj):
        return obj.user.username
