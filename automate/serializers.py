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
    user = serializers.SerializerMethodField()

    class Meta:
        """Meta class for Repository Serializer."""
        model = Repository
        exclude = ["created_at", "updated_at"]
        lookup_field = "slug"

    def get_user(self, obj):
        user = {
            "username": obj.owner.username,
            "email": obj.owner.email
        }
        return user
