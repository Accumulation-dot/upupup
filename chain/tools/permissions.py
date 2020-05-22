from rest_framework.permissions import BasePermission

from user import models


# 获取当前用户的数据
class Owned(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


#  获取不属于当前用户的数据
class UnOwned(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user != request.user

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class LevelPermission(BasePermission):
    message = '等级不够， 请联系管理员'

    def has_permission(self, request, view):
        user = models.CoinUser.objects.filter(id=request.user.id).first()
        return bool(user and user.level != 1)


class Identified(BasePermission):
    message = '请先进行身份验证, 才能进行操作'

    def has_permission(self, request, view):
        info = models.Identifier.objects.filter(user=request.user).first()
        return bool(info)
