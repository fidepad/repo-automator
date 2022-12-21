from rest_framework import serializers

from automate.models import Repository


class WebHookSerializer(serializers.Serializer):
    """Webhook Serializer."""

    class Meta:
        """Meta class for Webhook Serializer."""

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class RepositorySerializer(serializers.ModelSerializer):
    """Repository Serializer."""
    class Meta:
        """Meta class for Repository Serializer."""
        model = Repository
        fields = "__all__"
