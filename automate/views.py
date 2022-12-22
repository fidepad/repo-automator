import json

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, response, status, viewsets, filters

from automate.filtersets import RepositoryFilter
from automate.models import Project
from automate.serializers import RepositorySerializer


class WebHookListView(generics.GenericAPIView):
    """API View to receive payload from github."""

    def post(self, request):
        """This webhook receives payload from github whenever a PR is approved and merged"""
        content = json.loads(request.body)
        return response.Response(
            {"message": "success", "action": content.get("action")},
            status=status.HTTP_200_OK,
        )


class RepositoryViewSets(viewsets.ModelViewSet):
    """Repository ViewSets.
    Note: primary_repo_type and secondary_repo_type text choice fields of either github
    or gitbucket (for now). The default is github. Please ensure to provide (gitbucket or others)
    if you are pushing to a different version control.
    """
    serializer_class = RepositorySerializer
    queryset = Project.objects.all()
    lookup_field = "slug"
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = RepositoryFilter
    ordering_fields = ["id", "owner", "created_at", "updated_at"]
    search_fields = ["id", "slug", "primary_repo", "secondary_repo", "primary_repo_type", "secondary_repo_type"]

    def get_queryset(self):
        owner = self.request.user
        return Project.objects.filter(owner=owner)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["owner"] = self.request.user
        return context
