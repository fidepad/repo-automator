from rest_framework import serializers
from rest_framework.reverse import reverse

from accounts.serializers import UserSerializer

from automate.models import Project
from automate.tasks import add_hook_to_repo, init_run_git


class ProjectSerializer(serializers.ModelSerializer):
    """Project Serializer."""

    owner = UserSerializer(read_only=True)

    class Meta:
        """Metaclass for Project Serializer."""

        model = Project
        fields = "__all__"
        lookup_field = "slug"
        extra_kwargs = {"owner": {"read_only": True}}

    def create(self, validated_data):
        project = super().create(validated_data)

        domain = self.context["request"].domain
        path = reverse("project:project-webhook", args=(project.slug,))
        project_webhook_url = domain + path
        
        # TODO: Applied celery delay
        add_hook_to_repo.delay(
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
        # TODO: I don't understand the todo above
        return attrs


class RepoSerializer(serializers.Serializer):
    """Serializer for the Repository."""

    name = serializers.CharField()


class HeadSerializer(serializers.Serializer):
    """Head Serializer for the project that contains information about the branch and the repository."""

    ref = serializers.CharField()
    repo = RepoSerializer()


class PullRequestSerializer(serializers.Serializer):
    """Pull Request Serializer."""

    id = serializers.IntegerField()
    url = serializers.URLField()
    state = serializers.CharField()
    title = serializers.CharField()
    body = serializers.CharField()
    head = HeadSerializer()


class WebHookSerializer(serializers.Serializer):
    """Serializer to automate cloning process between repositories."""

    action = serializers.CharField()
    pull_request = PullRequestSerializer()

    def clone_push_make_pr(self, project, data):
        """This method runs the cloning and pushing process. This should be moved into tasks."""
        init_run_git.delay(project, data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        self.clone_push_make_pr(self.context.get("queryset"), data)
        return data
