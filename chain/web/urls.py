from django.urls import path
from . import views

urlpatterns = [
    path('register.html', views.register),
    path('download.html', views.download),
    path('version/', views.version),
]