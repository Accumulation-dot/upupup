from django.urls import path

from trade import views

urlpatterns = [
    # 获取所有的出售信息
    path('sell/list/', views.sell_list),
    # 获取自己的出售信息
    path('sell/mine/', views.sell_mine),
    # 发布出售信息
    path('sell/item/', views.sell_item),
    # 取消
    path('sell/cancel/', views.sell_cancel),
    # 确认
    path('sell/confirm/', views.sell_confirm),

    path('sell/order/', views.sell_order),
    path('sell/order/fill/', views.sell_order_fill),
    path('sell/order/mine/', views.sell_order_mine),

    path('sell/order/detail', views.sell_detail),

    # buy 获取所有收购信息
    path('buy/list/', views.buy_list),
    # 获取自己的收购信息
    path('buy/mine/', views.buy_mine),
    # 发布收购信息
    path('buy/item/', views.buy_item),

    path('buy/cancel/', views.buy_cancel),

    path('buy/fill/', views.buy_fill),

    #
    path('buy/order/', views.buy_order),
    path('buy/order/mine/', views.buy_order_mine),
    path('buy/order/confirm/', views.buy_order_confirm),
    path('price/', views.price),
]
