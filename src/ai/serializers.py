from rest_framework import serializers

from ai.models import AITemporalComment

from ai.services import AITemporalCommentService

class AITemporalCommentSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        attrs['created_by'] = self.context['request'].user

        return attrs

    class Meta:
        model = AITemporalComment
        fields = ('id', 'ticket', 'comment', 'content', 'created_at', 'app', 'is_validated')

    def update(self, instance, validated_data):
        tmp_comment = super(AITemporalCommentSerializer, self).update(instance, validated_data)

        service = AITemporalCommentService(tmp_comment=tmp_comment)
        service.update(validated_data)

        return tmp_comment


class RetrieverSerializer(serializers.Serializer):
    subject = serializers.CharField()