from typing import Any
from typing import Dict

from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model

from core.models import Ticket
from core.models import Comment
from core.models import GlobalConfig
from core.models import TicketHistory

from core.enums import TicketEvent

from ai.llm import handling_response_generation

User = get_user_model()


class TicketService:
    def __init__(self, ticket: Ticket = None):
        self.ticket = ticket
        self.global_config = GlobalConfig.load()

    @transaction.atomic()
    def create(self, data: Dict) -> Ticket:
        assigned_to = data.pop('assigned_to', None)

        self.ticket = Ticket.objects.create(**data)

        if assigned_to:
            self.ticket.assigned_to.set(assigned_to)

        TicketHistory.objects.create(
            ticket=self.ticket,
            event=TicketEvent.TICKET_OPENED,
        )

        if self.global_config.generate_ticket_response_with_ai:
            handling_response_generation(self.ticket.id, None, is_comment=False)

        return self.ticket


class CommentService:
    def __init__(self, comment: Comment = None):
        self.comment = comment
        self.global_config = GlobalConfig.load()

    @transaction.atomic()
    def create(self, data: Dict[str, Any]) -> Comment:
        self.comment = Comment.objects.create(**data)

        ticket = self.comment.ticket
        ticket.last_reply_at = timezone.now()
        ticket.save()

        if self.comment.created_by.is_staff is True:
            # Send notification
            pass

        TicketHistory.objects.create(
            ticket=self.comment.ticket,
            related_object=self.comment,
            event=TicketEvent.COMMENT_ADDED
        )

        if self.global_config.generate_ticket_response_with_ai:
            handling_response_generation(ticket_id=None, comment_id=self.comment.id, is_comment=True)

        return self.comment
