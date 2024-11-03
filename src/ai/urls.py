from django.urls import path, include

from rest_framework.routers import DefaultRouter


from ai.views import AITemporalCommentViewset
from ai.views import AIManagementViewSet

router = DefaultRouter()

router.register('ai_temporal_comments', AITemporalCommentViewset, basename='ai_temporal_comments')
router.register('management', AIManagementViewSet, basename='management')

urlpatterns = [
    path('', include(router.urls))
]
