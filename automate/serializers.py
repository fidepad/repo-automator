from rest_framework import serializers
from rest_framework.reverse import reverse

from .models import Project
from .utils import add_hook_to_repo


class ProjectSerializer(serializers.ModelSerializer):
    """Repository Serializer."""

    user = serializers.SerializerMethodField()

    class Meta:
        """Metaclass for Repository Serializer."""

        model = Project
        lookup_field = "slug"
        extra_kwargs = {"owner": {"read_only": True}}

    def create(self, validated_data):
        project = super().create(**validated_data)

        domain = self.context["request"].domain
        path = reverse("project:project-webhook", args=(project.slug,))
        project_webhook_url = domain + path

        add_hook_to_repo(
            project_webhook_url=project_webhook_url,
            webhook_url=self.instance.primary_repo_webhook_url,
            repo_type=self.instance.primary_repo_type,
            repo_token=self.instance.primary_repo_token,
        )
        return project

    def get_user(self, obj):
        """Gets the user information and returns the name and email address."""
        user = {"username": obj.owner.username, "email": obj.owner.email}
        return user

    def validate(self, attrs):
        owner = self.context.get("owner")
        attrs["owner"] = owner
        return attrs
