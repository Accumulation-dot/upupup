from django.urls import path
from machine import views

from user.views import UserCreation

urlpatterns = [
    path('list/', views.MachineView.as_view()),
    path('records/', views.RecordView.as_view()),
    path('record/<int:pk>/', views.RecordInfoView.as_view()),
    path('mine/', views.mine),
    path('order/', views.order),
    path('daily/', views.machine_task_all),
    path('cs/', views.customer_service),
]
