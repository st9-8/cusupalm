from rest_framework import viewsets

from core.models import Ticket
from core.models import Comment

from core.serializers import TicketSerializer
from core.serializers import CommentSerializer


class TicketViewset(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    http_method_names = ('get', 'post')
    queryset = Ticket.objects.all()


class CommentViewset(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    http_method_names = ('get', 'post')
    queryset = Comment.objects.all()