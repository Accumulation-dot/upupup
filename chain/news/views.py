from datetime import datetime

from django.db import IntegrityError
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from machine.models import machine_earn_count
from news import models as nsm
from news import serializers as nss
from coins import models as csm
from machine import models as mm
from tools.tools import CustomPagination


class NewsView(generics.ListAPIView):
    queryset = nsm.News.objects.all()
    permission_classes = ([IsAuthenticated])
    serializer_class = nss.NewsSerializer


@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def task_request(request, format=None):
    if request.method == 'POST':
        now = datetime.now()
        now_date = request.data.get('date')
        if now_date != now.strftime("%Y-%m-%d"):
            return Response('请开始新任务', status=status.HTTP_205_RESET_CONTENT)
        try:
            task = nsm.Task.objects.get(user=request.user, date=now.date())
            return Response('今日任务已完成', status=status.HTTP_200_OK)
        except nsm.Task.DoesNotExist:
            earn_count = mm.machine_earn_count(request.user)
            task = nsm.Task(user=request.user, earn=earn_count)
            task.save()
            csm.record_creation(user=request.user, point=earn_count, key='daily_task', desc='日常任务')
            return Response(nss.TaskSerializer(task).data, status=status.HTTP_201_CREATED)
    else:
        tasks = nsm.Task.objects.filter(user=request.user)
        pagination = CustomPagination()
        try:
            query = pagination.paginate_queryset(tasks, request)
            return pagination.get_paginated_response(nss.TaskSerializer(query, many=True).data)
        except NotFound as e:
            return Response('没有数据', status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_check(request, format=None):
    try:
        today = nsm.Task.objects.get(user=request.user, date=datetime.now().date())
        return Response(nss.TaskSerializer(today).data, status=status.HTTP_202_ACCEPTED)
    except nsm.Task.DoesNotExist as e:
        return Response(nss.TaskSerializer(nsm.Task(user=request.user,
                                                    date=datetime.now().date(),
                                                    earn=machine_earn_count(user=request.user))).data,
                        status=status.HTTP_200_OK)
