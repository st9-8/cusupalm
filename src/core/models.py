from django.db import models
from django.core.cache import cache
from django.db.utils import ProgrammingError
from django.db.utils import OperationalError
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from django_ckeditor_5.fields import CKEditor5Field

from core.enums import App
from core.enums import TicketType
from core.enums import TicketEvent

from core.base import BaseModel

User = get_user_model()


class Ticket(BaseModel):
    """
        Abstract base class of Ticket
    """
    title = models.CharField(_('Ticket title'), max_length=255)
    description = CKEditor5Field()
    solution = models.TextField(_('Ticket solution'), blank=True)
    ticket_type = models.CharField(max_length=255, choices=TicketType.choices(), default=TicketType.GENERAL)
    last_reply_at = models.DateTimeField(blank=True, null=True)
    closed_at = models.DateTimeField(blank=True, null=True, editable=False)
    open_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='opened_tickets')
    open_by_email = models.EmailField(blank=True, null=True, help_text='This field is used by the app to save the '
                                                                       'email of the user who opened a ticket via chatbot')
    closed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='closed_tickets', blank=True, null=True)
    assigned_to = models.ManyToManyField(User, blank=True,
                                         related_name='tickets_assigned')
    notes = models.TextField(_('Agent notes'), blank=True)
    is_closed = models.BooleanField(default=False)
    is_draft = models.BooleanField(default=True)
    need_attention = models.BooleanField(default=False)
    app = models.CharField(max_length=255, choices=App.choices(), default=App.TAVILY)

    def __str__(self):
        return self.title

    def clean(self):
        if self.open_by.is_staff is True:
            raise ValidationError({
                'open_by': 'Only customer user are allowed to open ticket'
            })

        # Check if there are any assigned users
        if self.pk:  # Only check if the object has been saved (has a primary key)
            assigned_users = self.assigned_to.all()
            non_staff_users = assigned_users.filter(is_staff=False)

            if non_staff_users.exists():
                non_staff_usernames = ", ".join(user.username for user in non_staff_users)
                raise ValidationError(
                    {
                        'assigned_to': f"All assigned users must be staff members. "
                                       f"The following users are not staff: {non_staff_usernames}"
                    }
                )

    def get_history(self, except_last=False):
        """
            This function is used to get history directly from comments as dict
        """
        comments = self.comments.order_by('created_at')

        history = {
            'title': self.title,
            'initial_message': self.description,
            'thread': []
        }

        if comments.exists():
            if except_last:
                comments = comments.exclude(id=comments.last().id)

            for comment in comments:
                history['thread'].append({
                    'role': 'agent' if comment.created_by.is_staff else 'customer',
                    'text': comment.content
                })

        return history

    class Meta:
        ordering = ['-updated_at']


class Comment(BaseModel):
    """
        Comment on ticket
    """
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    content = CKEditor5Field()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    is_solution = models.BooleanField(default=False)
    last_reply_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.content[:10]}...'

    def creator(self):
        return str(self.created_by)

    creator.short_description = 'Creator of the comment'

    class Meta:
        verbose_name = _('Ticket comment')
        verbose_name_plural = _('Ticket comments')
        indexes = [
            models.Index(fields=['created_by'])
        ]
        ordering = ('-created_at',)


class TicketHistory(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='histories')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)
    related_id = models.CharField(max_length=255, blank=True, null=True)
    related_object = GenericForeignKey('content_type', 'related_id')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    event = models.CharField(_('Event happened on the ticket'), max_length=255, choices=TicketEvent.choices())
    previous_status = models.CharField(_('Previous status'), max_length=255, blank=True, null=True)
    current_status = models.CharField(_('Current status'), max_length=255, blank=True, null=True)

    def __str__(self):
        return self.event

    class Meta:
        verbose_name = _('History')
        verbose_name_plural = _('Histories')
        ordering = ['-created']


class Singleton(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super(Singleton, self).save(*args, **kwargs)
        self.set_cache()

    def delete(self, using=None, keep_parents=False):
        raise ValidationError(_('Unable to delete this model'))

    def set_cache(self):
        cache.set(self.__class__.__name__, self)

    @classmethod
    def load(cls):
        from django.db import connection

        if 'core_globalconfig' not in connection.introspection.table_names():
            return

        try:
            if cache.get(cls.__name__) is None:
                unique_instance, created = cls.objects.get_or_create(pk=1)
                if not created:
                    unique_instance.set_cache()
        except (ProgrammingError, OperationalError) as e:
            pass

        return cache.get(cls.__name__)


class GlobalConfig(Singleton):
    """
        This model will handle all global config linked to the project.
    """

    generate_ticket_response_with_ai = models.BooleanField(default=True,
                                                           help_text='Define if yes or no the response for each ticket has to be generated by the ')

    def __str__(self):
        return 'Global configuration'

    class Meta:
        ordering = ['-id']
