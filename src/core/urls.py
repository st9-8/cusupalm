from django.urls import path, include

from rest_framework.routers import DefaultRouter

from core.views import TicketViewset
from core.views import CommentViewset

router = DefaultRouter()

router.register('tickets', TicketViewset, basename='tickets')
router.register('comments', CommentViewset, basename='comments')

urlpatterns = [
    path('', include(router.urls))
]
