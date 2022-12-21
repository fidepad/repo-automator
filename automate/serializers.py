from django.db import IntegrityError
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
        extra_kwargs = {
            "owner": {"read_only": True},
            "primary_repo_type": {"required": True},
            "secondary_repo_type": {"required": True},
        }

    def get_user(self, obj):
        user = {
            "username": obj.owner.username,
            "email": obj.owner.email
        }
        return user

    def create(self, validated_data):
        owner = self.context.get("owner")
        validated_data["owner"] = owner
        try:
            result = super(RepositorySerializer, self).create(validated_data)
            return result
        except IntegrityError:
            raise serializers.ValidationError({"message": "Primary & Secondary Repo names exists. Please rename!"})
