from core.base import CustomEnum


class TicketType(CustomEnum):
    BUG = 'BUG'
    ISSUE = 'ISSUE'
    GENERAL = 'GENERAL'
    ENHANCEMENT = 'ENHANCEMENT'


class TicketEvent(CustomEnum):
    TICKET_OPENED = 'ticket_opened'
    ATTACHMENT_ADDED = 'attachment_added'
    ATTACHED_REMOVED = 'attachment_removed'
    COMMENT_ADDED = 'comment_added'
    COMMENT_REMOVED = 'comment_removed'
    ARTICLE_ADDED_AS_SOLUTION = 'article_added_as_solution'
    ARTICLE_REMOVED_AS_SOLUTION = 'article_removed_as_solution'
    STATUS_CHANGED = 'status_changed'
    TICKET_CLOSED = 'ticket_closed'
    TICKET_REOPENED = 'ticket_reopened'


class App(CustomEnum):
    TAVILY = 'TAVILY'
