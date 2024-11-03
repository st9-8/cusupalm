import logging
from traceback_with_variables import format_exc

logger = logging.getLogger()


def handling_ai_validation_email_to_customer(comment_id: int):
    """
        The aim of this task is to send back the response to the customer who created the request initially
    """
    from core.models import Comment
    from core.utils import send_simple_mail

    try:
        comment = Comment.objects.get(id=comment_id)

        subject = f"Re: {comment.ticket.title}"
        send_simple_mail(to=comment.ticket.open_by_email, subject=subject, message=comment.content)

        return True
    except Comment.DoesNotExist as e:
        logger.error(f'Comment {comment_id} not found')
        return False
    except Exception as e:
        logger.error(format_exc(e))
        return False
