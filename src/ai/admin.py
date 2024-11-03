from django.contrib import admin

from ai.models import AIResource
from ai.models import AITemporalComment


@admin.register(AIResource)
class AIResourceAdmin(admin.ModelAdmin):
    pass


@admin.register(AITemporalComment)
class AITemporalCommentAdmin(admin.ModelAdmin):
    pass
