from django_filters.rest_framework import FilterSet

from automate.models import Project


class RepositoryFilter(FilterSet):
    """Repository Filterset Class."""

    class Meta:
        """Metaclass for Repository Filterset Class."""

        model = Project
        # fmt: off
        fields = [
            "owner",
            "name",
            "slug",
            "primary_repo_owner",
            "primary_repo_name",
            "primary_repo_token",
            "primary_repo_type",
            "primary_repo_project_name",
            "secondary_repo_owner",
            "secondary_repo_name",
            "secondary_repo_token",
            "secondary_repo_type",
            "secondary_repo_project_name",
        ]
