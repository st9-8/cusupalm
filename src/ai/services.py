import logging
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError

from traceback_with_variables import format_exc

from ai.models import AITemporalComment
from core.enums import TicketEvent

from core.models import Comment
from core.models import TicketHistory

from ai.utils import handling_ai_validation_email_to_customer


class AITemporalCommentService:
    def __init__(self, tmp_comment: AITemporalComment):
        self.tmp_comment = tmp_comment
        self.logger = logging.getLogger()

    def create(self, data):
        pass

    @transaction.atomic()
    def update(self, data):
        try:
            if data.get('is_validated') is True:
                # Means that the proposal is going to be validated, so create the corresponding comment
                ai_comment = Comment.objects.create(
                    ticket=self.tmp_comment.ticket if self.tmp_comment.ticket else self.tmp_comment.comment.ticket,
                    content=self.tmp_comment.content,
                    created_by=data.get('created_by'),
                    role='agent'
                )

                ticket = ai_comment.ticket
                ticket.updated_at = timezone.now()
                ticket.last_reply_at = timezone.now()
                ticket.save()

                TicketHistory.objects.create(
                    ticket=ai_comment.ticket,
                    related_object=ai_comment,
                    event=TicketEvent.COMMENT_ADDED
                )

                r = handling_ai_validation_email_to_customer(ai_comment.id)
                if not r:
                    self.logger.warning(
                        f'Unable to send notification for comment #{ai_comment.id} to {ai_comment.ticket.open_by_email}')
        except Exception as e:
            self.logger.error(format_exc(e))
            raise ValidationError(f'Unable to handle update of the AI proposal #{self.tmp_comment.id}')
