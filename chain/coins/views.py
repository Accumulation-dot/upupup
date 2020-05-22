# Create your views here.
from rest_framework.decorators import permission_classes, api_view
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from coins import models as csm
from coins.serializer import RecordSerializer, RuleSerializer
from tools import tools
from tools.permissions import Owned


@api_view(['GET', ])
@permission_classes([Owned, ])
def record_list(request, format=None):
    records = csm.Record.objects.filter(user=request.user).order_by('-datetime')
    pagination = tools.CustomPagination()
    query = pagination.paginate_queryset(records, request)
    return pagination.get_paginated_response(RecordSerializer(query, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def coin(request, format=None):
    return Response(csm.query_coin(request.user))


class RuleView(ListAPIView):
    queryset = csm.CoinRule.objects.filter(used=True)
    permission_classes = ([AllowAny])
    serializer_class = RuleSerializer
