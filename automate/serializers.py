from django.conf import settings
from rest_framework import serializers
from rest_framework.reverse import reverse
from django.forms.models import model_to_dict
from accounts.serializers import UserSerializer
from automate.choices import RepoTypeChoices
from automate.models import Project
from automate.tasks import add_hook_to_repo_task, init_run_git
from automate.encryptor import Crypt
from automate.utils import refresh_bitbucket_token
from repo.utils import MakeRequest

crypt = Crypt()


class ProjectSerializer(serializers.ModelSerializer):
    """Project Serializer."""

    owner = UserSerializer(read_only=True)

    class Meta:
        """Metaclass for Project Serializer."""

        model = Project
        fields = "__all__"
        lookup_field = "slug"
        extra_kwargs = {"owner": {"read_only": True}}

    def validate_bitbucket_tokens(self, category="secondary"):
        """This ensures Bitbucket repositories get Refresh Token, Client ID and Secrets needed for refreshing
        bitbucket access token.
        """
        data = self.validated_data

        refresh_token = data.get(f"{category}_refresh_token")
        client_id = data.get(f"{category}_client_id")
        client_secret = data.get(f"{category}_client_secret")

        # Run a loop through this array and raise a validation error if any is empty
        credentials = {
            "refresh_token": refresh_token,
            "client_secret": client_secret,
            "client_id": client_id,
        }
        errors = []

        for key, value in credentials.items():
            if not value:
                errors.append(
                    f"{category}_{key} is necessary for {category.title()} Bitbucket Authentication."
                )

        if errors:
            raise serializers.ValidationError({"error": errors})

    def validate_repo(self, attrs):
        """This method was created to be used on create because the repo validation runs even when
        user wants to update project and it fails on testing as the parameters weren't provided.
        """
        primary_user = attrs["primary_repo_owner"]
        primary_repo = attrs["primary_repo_name"]
        primary_type = attrs.get("primary_repo_type")
        primary_credentials = {
            "token": attrs["primary_repo_token"],
            "client_id": attrs.get("primary_client_id"),
            "client_secret": attrs.get("primary_client_secret"),
            "refresh_token": attrs.get("primary_refresh_token"),
        }

        secondary_user = attrs["secondary_repo_owner"]
        secondary_repo = attrs["secondary_repo_name"]
        secondary_type = attrs.get("secondary_repo_type")
        secondary_credentials = {
            "token": attrs.get("secondary_repo_token"),
            "client_id": attrs.get("secondary_client_id"),
            "client_secret": attrs.get("secondary_client_secret"),
            "refresh_token": attrs.get("secondary_refresh_token"),
        }

        # Ensure refresh token, client id and secret are provided for bitbucket authentication
        if primary_type == RepoTypeChoices.BITBUCKET.value:
            self.validate_bitbucket_tokens("primary")
        if secondary_type == RepoTypeChoices.BITBUCKET.value:
            self.validate_bitbucket_tokens()

        # Validate the owner/token/repo name are all correct and can connect to Repository

        test_primary_repo = self.test_if_repo_exists(
            primary_type, primary_credentials, primary_repo, primary_user
        )
        if test_primary_repo != "ok":
            error = {
                "error": "Primary repository not accessible",
                "message": test_primary_repo,
            }
            raise serializers.ValidationError(error)

        test_secondary_repo = self.test_if_repo_exists(
            secondary_type, secondary_credentials, secondary_repo, secondary_user
        )
        if test_secondary_repo != "ok":
            error = {
                "error": "Secondary repository not accessible",
                "info": test_secondary_repo,
            }
            raise serializers.ValidationError(error)

    def create(self, validated_data):
        # Validate repositories here
        self.validate_repo(validated_data)

        # project_ = super().create(validated_data)
        project_ = Project.objects.last()
        context = self.context["request"]
        domain = context.domain
        user_ = UserSerializer(context.user).data
        path = reverse("project:project-webhook", args=(project_.slug,))
        project_webhook_url = domain + path

        project = ProjectSerializer(project_)
        # TODO: Applied celery delay
        add_hook_to_repo_task.delay(
            project_webhook_url,
            user_["email"],
            project.data,
        )
        return project_

    def test_if_repo_exists(self, git_type, credentials: dict, repo, owner):
        """This ensures the repository url is accessible."""

        credentials = crypt.multi_decrypt(credentials)
        token = credentials["token"]

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
        if not isinstance(response, dict):
            status_code = response.status_code
            if status_code == 200:
                return "ok"
            if status_code == 401 and git_type == RepoTypeChoices.BITBUCKET.value:
                # Attempt to get a new access token for bitbucket user
                access_token = refresh_bitbucket_token(credentials)
                if isinstance(access_token, str):
                    # Here we try to access the bitbucket repository with the new access token.
                    header = {"Authorization": f"Bearer {access_token}"}
                    req = MakeRequest(url, headers=header)
                    response = req.get()
                    status_code = response.status_code
                    if status_code == 200:
                        return "ok"
                else:
                    result = {
                        "error": "Access token is invalid and Refresh Token is not working",
                        "details": access_token,
                    }
                    raise serializers.ValidationError(result)
            # It returns the error message if it's not 200
            return response.json()
        return response

    def encrypt_credentials(self, data):
        """This function encrypts credentials if they are provided."""

        initial_data = {
            "primary_repo_token": data.get("primary_repo_token"),
            "primary_client_id": data.get("primary_client_id"),
            "primary_client_secret": data.get("primary_client_secret"),
            "primary_refresh_token": data.get("primary_refresh_token"),
            "secondary_repo_token": data.get("secondary_repo_token"),
            "secondary_client_id": data.get("secondary_client_id"),
            "secondary_client_secret": data.get("secondary_client_secret"),
            "secondary_refresh_token": data.get("secondary_refresh_token"),
        }

        # Use a loop to update the data i.e., This helps to pass validation during updating
        for key, value in initial_data.items():
            if value:
                data[key] = crypt.encrypt(value)

        return data

    def validate(self, attrs):
        owner = self.context.get("owner")
        attrs["owner"] = owner

        # Encrypt necessary credentials
        attrs = self.encrypt_credentials(attrs)
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
    body = serializers.CharField(allow_blank=True, required=False, allow_null=True)
    head = HeadSerializer()


class WebHookSerializer(serializers.Serializer):
    """Serializer to automate cloning process between repositories."""

    action = serializers.CharField()
    pull_request = PullRequestSerializer()

    def clone_push_make_pr(self, project, data):
        """This method runs the cloning and pushing process. This should be moved into tasks."""
        init_run_git(project, data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        self.clone_push_make_pr(self.context.get("queryset"), data)
        return data
