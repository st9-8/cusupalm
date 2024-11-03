from __future__ import annotations

import logging
from typing import List

from django.conf import settings
from django.core.mail import send_mail

from traceback_with_variables import format_exc

logger = logging.getLogger()


def send_simple_mail(to: str | List, subject: str, message: str) -> None:
    """Send a simple plain text email"""
    from_email = settings.FROM_EMAIL
    recipients = to.split(',') if isinstance(to, str) else to

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipients,
            fail_silently=False,
        )
    except Exception as e:
        logger.error(format_exc(e))
        raise e
