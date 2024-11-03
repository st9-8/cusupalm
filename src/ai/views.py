import logging

from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAdminUser

from drf_yasg.utils import swagger_auto_schema

from traceback_with_variables import format_exc

from core.pagination import PaginationWithTotalPage

from ai.models import AITemporalComment
from ai.serializers import AITemporalCommentSerializer
from ai.serializers import RetrieverSerializer

from ai.retrievers.tavily import TavilyRetriever


logger = logging.getLogger()

class AITemporalCommentViewset(viewsets.ModelViewSet):
    queryset = AITemporalComment.objects.all()
    serializer_class = AITemporalCommentSerializer
    pagination_class = PaginationWithTotalPage
    http_method_names = ('get', 'patch')
    permission_classes = (IsAuthenticated, IsAdminUser)


class AIManagementViewSet(viewsets.ViewSet):
    """
        Management views for AI app
    """
    serializer_class = None
    permission_classes = [IsAuthenticated, IsAdminUser]

    @swagger_auto_schema(methods=['post'], request_body=RetrieverSerializer)
    @action(detail=False, methods=['post'])
    def run_retrievers(self, request, *args, **kwargs):
        """
        Run the retrievers to fetch and process data
        """
        try:

            retriever = TavilyRetriever()
            articles = retriever.get_articles(subject=request.data.get('subject'))
            retriever.embed_articles(articles=articles)

            return Response(status=status.HTTP_200_OK)
        except ValueError as e:
            logger.error(format_exc(e))
            raise ValidationError(str(e))
        except Exception as e:
            logger.error(format_exc(e))
            raise APIException('Something went wrong while running the retrievers')
