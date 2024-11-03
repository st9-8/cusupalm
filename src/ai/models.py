from django.db import models
from django.utils.translation import gettext_lazy as _

from core.base import BaseModel

from core.models import Ticket
from core.models import Comment

from ai.enums import DataType

from core.enums import App

from django_ckeditor_5.fields import CKEditor5Field


class AIResource(models.Model):
    app = models.CharField(max_length=255)
    link = models.URLField(blank=True, null=True)
    original_document = models.FileField(blank=True, null=True, upload_to='ai_resources/',
                                         verbose_name='ai resources')
    data_type = models.CharField(max_length=255, choices=DataType.choices(), default=DataType.TEXT,
                                 help_text='This field contains type of data stored, Raw Text, PDF, MarkDown, Web link')
    content = models.TextField(blank=True, null=True)
    metadata = models.JSONField(blank=True, null=True)


class AITemporalComment(BaseModel):
    """
        This is a proposal response for the ticket, response provided by LLM
    """

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='ai_proposals', blank=True, null=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='ai_proposals', blank=True, null=True)
    content = CKEditor5Field()
    is_validated = models.BooleanField(default=False)
    app = models.CharField(max_length=255, choices=App.choices(), default=App.TAVILY)

    def __str__(self):
        return f'{self.content[:10]}...'

    class Meta:
        verbose_name = _('AI Response proposal')
        verbose_name_plural = _('AI Response proposals')
        ordering = ('-created_at',)
