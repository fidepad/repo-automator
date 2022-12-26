from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets, status
from rest_framework.response import Response
import requests
import json
from .filtersets import RepositoryFilter
from .models import Project
from .serializers import ProjectSerializer


def add_hook_to_repo(repo, host, owner, auth_token):
    endpoint = f'https://api.github.com/repos/{owner}/{repo}/hooks'
    payload = {
        "name": "web",
        "active": True,
        "events": ["push", "pull_request"],
        "config": {
            "url": f"https://{host}/hooks/{repo}/",
            "content_type": "json",
            "insecure_ssl": "0"}
    }
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {auth_token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    try:
        response = requests.post(endpoint, data=json.dumps(payload), headers=headers)
    except Exception as e:
        raise Exception(e)
    if response.status_code == 201:
        return True
    return False


class ProjectViewSets(viewsets.ModelViewSet):
    """Project Repository ViewSets.

    Note: primary_repo_type and secondary_repo_type text choice fields of either github
    or gitbucket (for now). The default is github. Please ensure to provide (gitbucket or others)
    if you are pushing to a different version control.
    """

    serializer_class = ProjectSerializer
    queryset = Project.objects.all()
    lookup_field = "slug"
    # Added filter backends to settings and they stopped working along with knox auth
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = RepositoryFilter
    search_fields = [
        "id",
        "name",
        "slug",
        "primary_repo",
        "secondary_repo",
        "primary_repo_type",
        "secondary_repo_type",
    ]

    def get_queryset(self):
        owner = self.request.user
        return Project.objects.filter(owner=owner)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["owner"] = self.request.user
        return context

    def create(self, request, *args, **kwargs):
        data = self.serializer_class(data=request.data)
        data.is_valid(raise_exception=True)
        try:
            repo_name = data.validated_data['primary_repo']
            repo_name = str(repo_name).split('/')
            repo_name = repo_name[-1]
            repo_name = repo_name.split('.')[0]
        except Exception as e:
            raise Exception(e)
        host = request.get_hosts()
        if add_hook_to_repo(
            repo=repo_name,
            hook=host,
            owner=data.validated_data['owner'],
            auth_token=data.validated_data['token']
        ):
            return super().create(request, *args, **kwargs)
        return Response(
            {
                'error': 'An error occurred, make sure valid data is provided'
            }, status=status.HTTP_400_BAD_REQUEST
        )
