from django.urls import path

from pay import views as pv

urlpatterns = [
    path('all/', pv.pay),

    path('bank/', pv.bank),
    path('ali/', pv.ali_pay),
    # pv.PayView.as_view()),
    path('<int:pk>/', pv.pay_update),
    # pv.PayDetailView.as_view()),
]