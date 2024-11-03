from django.contrib import admin
from pydantic_core.core_schema import model_field

from core.models import Ticket
from core.models import Comment
from core.models import GlobalConfig


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('title', 'open_by', 'is_closed', 'created_at')
    list_filter = ('is_closed', 'is_draft', 'need_attention', 'ticket_type')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'created_by', 'created_at')
    list_filter = ('is_solution',)

@admin.register(GlobalConfig)
class GlobalConfigAdmin(admin.ModelAdmin):
    pass