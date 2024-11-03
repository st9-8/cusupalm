from django.contrib.auth import get_user_model

from rest_framework import serializers

from core.models import Ticket
from core.models import Comment

from core.services import TicketService
from core.services import CommentService

User = get_user_model()


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id', 'ticket', 'content')
        read_only_fields = ('created_by', 'is_solution', 'last_reply_at')

    def validate(self, attrs):
        if 'content' not in attrs:
            raise serializers.ValidationError('Content field is required to update.')

        if attrs['ticket'].is_closed:
            raise serializers.ValidationError('This ticket is already closed.')

        attrs['created_by'] = self.context['request'].user

        return attrs

    def create(self, validated_data):
        service = CommentService()
        comment = service.create(validated_data)

        return comment


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = (
            'id', 'title', 'description', 'ticket_type', 'assigned_to', 'notes', 'need_attention', 'open_by_email',
            'is_closed', 'app')
        read_only_fields = ('solution', 'last_reply_at', 'open_by', 'open_by_email', 'is_closed', 'app')

    def get_comments(self, instance):
        serializer = CommentSerializer(instance.comments.all(), many=True)

        return serializer.data

    def validate(self, attrs):
        if 'assigned_to' in attrs:
            assigned = []
            for email in attrs['assigned_to']:
                try:
                    user_assigned = User.objects.get(email=email, is_staff=True)
                    assigned.append(user_assigned.id)
                except User.DoesNotExist as e:
                    raise serializers.ValidationError(f"Seller {email} doesn't exist") from e

            if self.context['request'].user.is_staff is True:
                raise serializers.ValidationError('Only non -taff user must open ticket')

            attrs['assigned_to'] = assigned
        attrs['open_by'] = self.context['request'].user
        attrs['open_by_email'] = self.context['request'].user.email

        return attrs

    def create(self, validated_data):
        service = TicketService()

        ticket = service.create(validated_data)

        return ticket
