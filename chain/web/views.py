from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from web.models import AppVersion
from web.serializers import AppVersionS


def register(request):
    return render(request, 'register.html')


def download(request):
    return render(request, 'download.html')


@api_view(['GET'])
@permission_classes([AllowAny])
def version(request, format=None):
    v = AppVersion.objects.all().first()
    return Response(AppVersionS(v).data)
