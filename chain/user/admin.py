from django.contrib import admin

from user.models import CoinUserInfo, CoinUser, Address, Identifier


# Register your models here.


@admin.register(CoinUser)
class CoinUser(admin.ModelAdmin):
    list_display = ('username',)


@admin.register(CoinUserInfo)
class CoinUserInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', )


@admin.register(Identifier)
class IdentifierAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'number',)
