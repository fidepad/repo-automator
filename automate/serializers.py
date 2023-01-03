from rest_framework import serializers
from django.core.exceptions import ValidationError
from .models import Project
from .utils import add_hook_to_repo, gen_hook_url


class ProjectSerializer(serializers.ModelSerializer):
    """Repository Serializer."""
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
            raise ValidationError({'error': 'this repo bundle was not initialized'})
        try:
            repo_name = validated_data['primary_repo']
            repo_name = str(repo_name).split('/')
            repo_name = repo_name[-1]
            repo_name = repo_name.split('.')[0]
        except ValueError as err:
            raise Exception(err)
        host = gen_hook_url(username=validated_data['owner'].username, repo_name=repo_name)
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
