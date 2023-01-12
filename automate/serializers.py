from django.conf import settings
from rest_framework import serializers
from rest_framework.reverse import reverse

from accounts.serializers import UserSerializer
from automate.choices import RepoTypeChoices
from automate.models import Project
from automate.tasks import add_hook_to_repo_task, init_run_git
from repo.utils import MakeRequest


class ProjectSerializer(serializers.ModelSerializer):
    """Project Serializer."""

    owner = UserSerializer(read_only=True)

    class Meta:
        """Metaclass for Project Serializer."""

        model = Project
        fields = "__all__"
        lookup_field = "slug"
        extra_kwargs = {"owner": {"read_only": True}}

    def validate_repo(self, attrs):
        """This method was created to be used on create because the repo validation runs even when
        user wants to update project and it fails on testing as the parameters weren't provided.
        """
        primary_user = attrs["primary_repo_owner"]
        primary_token = attrs["primary_repo_token"]
        primary_repo = attrs["primary_repo_name"]
        primary_type = attrs.get("primary_repo_type")

        secondary_user = attrs["secondary_repo_owner"]
        secondary_token = attrs["secondary_repo_token"]
        secondary_repo = attrs["secondary_repo_name"]
        secondary_type = attrs.get("secondary_repo_type")

        # Validate the owner/token/repo name are all correct and can connect to Repository

        test_primary_repo = self.test_if_repo_exists(
            primary_type, primary_token, primary_repo, primary_user
        )
        if test_primary_repo != "ok":
            error = {
                "error": "Primary repository not accessible",
                "message": test_primary_repo,
            }
            raise serializers.ValidationError(error)

        test_secondary_repo = self.test_if_repo_exists(
            secondary_type, secondary_token, secondary_repo, secondary_user
        )
        if test_secondary_repo != "ok":
            error = {
                "error": "Secondary repository not accessible",
                "info": test_primary_repo,
            }
            raise serializers.ValidationError(error)

    def create(self, validated_data):
        project = super().create(validated_data)

        domain = self.context["request"].domain
        path = reverse("project:project-webhook", args=(project.slug,))
        project_webhook_url = domain + path

        # Validate repositories here
        self.validate_repo(validated_data)

        # TODO: Applied celery delay
        add_hook_to_repo_task.delay(
            project_webhook_url=project_webhook_url,
            webhook_url=project.primary_repo_webhook_url,
            repo_type=project.primary_repo_type,
            repo_token=project.primary_repo_token,
        )
        return project

    def test_if_repo_exists(self, git_type, token, repo, owner):
        """This ensures the repository url is accessible."""

        # setup Url
        if git_type == RepoTypeChoices.BITBUCKET.value:
            url = f"{settings.BITBUCKET_BASE_URL}/repositories/{owner}/{repo}"
            header = {"Authorization": f"Bearer {token}"}
        else:
            url = f"{settings.GITHUB_BASE_URL}/repos/{owner}/{repo}"
            header = {"Authorization": f"Token {token}"}

        # Test Repository
        url = url.replace(" ", "-").strip().lower()
        req = MakeRequest(url, headers=header)
        response = req.get()
        if isinstance(response, dict):
            if response.status_code == 200:
                return "ok"
            # It returns the error message if it's not 200
            return response.json()
        return response

    def validate(self, attrs):
        owner = self.context.get("owner")
        attrs["owner"] = owner
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
