from collections import OrderedDict

from django.db.models import Count, Q
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from pay.models import payment_count
from user.models import ident_count


class CustomPagination(PageNumberPagination):
    page_size = 20
    max_page_size = 30
    page_query_param = 'page'
    page_size_query_param = 'size'

    def get_paginated_response(self, data):
        next_link = self.get_next_link()
        next_response = '0'
        if next_link:
            next_response = '1'
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', next_response),
            ('list', data)
        ]))


def request_error(errors, r_status=status.HTTP_400_BAD_REQUEST):
    return Response(data=errors, status=r_status)


def request_response(data, error, message):
    if error:
        return Response(data=error,
                        status=status.HTTP_400_BAD_REQUEST)
    if not data:
        return Response(data={'code': 1, 'message': message})
    return Response(data={'code': 0, 'message': "ok", 'data': data})


def ip_address(request):
    """
    获取ip地址
    :param request:
    :return:
    """
    ip = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if not ip:
        ip = request.META.get('REMOTE_ADDR', "")
    client_ip = ip.split(",")[-1].strip() if ip else ""
    return client_ip


def identified(user):
    return payment_count(user=user) > 0 and ident_count(user=user) > 0
