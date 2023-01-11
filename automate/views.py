from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .filtersets import RepositoryFilter
from .models import Project
from .serializers import ProjectSerializer, WebHookSerializer


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

    @action(detail=False, methods=["POST"], url_path="(?P<slug>[\w-]+)/webhook")
    def webhook(self, request, slug):
        queryset = get_object_or_404(Project, slug=slug)
        serializer = WebHookSerializer(
            data=request.data, context={"queryset": queryset}
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
