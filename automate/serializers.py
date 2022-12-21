from rest_framework import serializers


class WebHookSerializer(serializers.Serializer):
    """Webhook Serializer."""

    class Meta:
        """Meta class for Webhook Serializer."""

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
