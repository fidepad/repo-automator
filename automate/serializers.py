from rest_framework import serializers
from rest_framework.reverse import reverse

from accounts.serializers import UserSerializer

from .models import Project
from .utils import add_hook_to_repo


class ProjectSerializer(serializers.ModelSerializer):
    """Repository Serializer."""

    owner = UserSerializer(read_only=True)

    class Meta:
        """Metaclass for Repository Serializer."""

        model = Project
        fields = "__all__"
        lookup_field = "slug"
        extra_kwargs = {"owner": {"read_only": True}}

    def create(self, validated_data):
        project = super().create(validated_data)

        domain = self.context["request"].domain
        path = reverse("project:project-webhook", args=(project.slug,))
        project_webhook_url = domain + path
        # TODO: Move this logic to celery
        add_hook_to_repo(
            project_webhook_url=project_webhook_url,
            webhook_url=project.primary_repo_webhook_url,
            repo_type=project.primary_repo_type,
            repo_token=project.primary_repo_token,
        )
        return project

    def validate(self, attrs):
        owner = self.context.get("owner")
        attrs["owner"] = owner
        # TODO: Validate the owner/token/repo name are all correct and can connect to Repository
        return attrs
