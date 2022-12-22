from django.db import IntegrityError
from rest_framework import serializers

from automate.models import Project


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

        model = Project
        exclude = ["created_at", "updated_at"]
        lookup_field = "slug"
        extra_kwargs = {
            "owner": {"read_only": True},
            "primary_repo_type": {"required": True},
            "secondary_repo_type": {"required": True},
        }

    def get_user(self, obj):
        """Gets the user information and returns the name and email address."""
        user = {"username": obj.owner.username, "email": obj.owner.email}
        return user

    def create(self, validated_data):
        owner = self.context.get("owner")
        validated_data["owner"] = owner
        try:
            result = super().create(validated_data)
            return result
        except IntegrityError as err:
            raise serializers.ValidationError(
                {"message": "Integrity Error", "detail": str(err)}
            )
