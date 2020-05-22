"""chain URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import static
from django.contrib import admin
from django.urls import path, include
from rest_framework.documentation import include_docs_urls
from rest_framework.urlpatterns import format_suffix_patterns

from chain import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path(r'docs/', include_docs_urls(title='接口文档')),
    path('user/', include('user.urls'),),
    path('news/', include('news.urls'),),
    path('coins/', include('coins.urls'),),
    path('trade/', include('trade.urls'),),
    path('machine/', include('machine.urls'),),
    path('advert/', include('advert.urls'),),
    path('pay/', include('pay.urls'),),
    path('', include('web.urls'),),
]

urlpatterns = format_suffix_patterns(urlpatterns)

urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static.static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)