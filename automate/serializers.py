from rest_framework import serializers
from django.core.exceptions import ValidationError
from .models import Project, History
from repo.utils import add_hook_to_repo, gen_hook_url
from automate.gitremote import GitRemote


class ProjectSerializer(serializers.ModelSerializer):
    """Repository Serializer."""
    # token = serializers.CharField(write_only=True)
    user = serializers.SerializerMethodField()

    class Meta:
        """Meta class for Repository Serializer."""

        model = Project
        exclude = ["created_at", "updated_at"]
        lookup_field = "slug"
        extra_kwargs = {"owner": {"read_only": True}}

    def create(self, validated_data):
        repo = super().create(validated_data)
        if not repo:
            raise serializers.ValidationError({'error': 'this repo bundle was not initialized'})
        try:
            repo_name = validated_data['primary_repo']
            repo_name = str(repo_name).split('/')
            repo_name = repo_name[-1]
            repo_name = repo_name.split('.')[0]
        except ValueError as err:
            raise Exception(err)
        host = gen_hook_url(username=validated_data['owner'].get('username'), repo_name=repo_name)
        if add_hook_to_repo(
            repo=repo_name,
            hook=host,
            owner=validated_data['owner'],
            auth_token=validated_data['token']
        ):
            return repo
        raise ValueError({'error': 'please reinitialize repository bundle'})

    def get_user(self, obj):
        """Gets the user information and returns the name and email address."""
        user = {"username": obj.owner.username, "email": obj.owner.email}
        return user

    def validate(self, attrs):
        owner = self.context.get("owner")
        attrs["owner"] = owner
        return attrs


class HeadSerializer(serializers.Serializer):
    """Head serializer."""
    ref = serializers.CharField()


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

    def clone_process(self, project, data):
        """This method runs the cloning process. This should be moved into tasks."""
        primary_access = "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" # Supposed to be coming from project
        secondary_access = "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"
        git = GitRemote(
            primary_access=primary_access,
            primary_url=project.primary_repo_url,
            primary_type=project.primary_repo_type,
            secondary_access=secondary_access,
            secondary_url=project.secondary_repo_url,
            secondary_type=project.secondary_repo_type,
            project=project.slug,
            branch_name=data.get("pull_request").get('head').get('ref')
        )

    def to_representation(self, instance):
        data = super(WebHookSerializer, self).to_representation(instance)
        self.clone_process(self.context.get('queryset'), data)
        return data
