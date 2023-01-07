from django_filters.rest_framework import FilterSet

from automate.models import Project


class RepositoryFilter(FilterSet):
    """Repository Filterset Class."""

    class Meta:
        """Meta class for Repository Filterset Class."""

        model = Project
        # fmt: off
        fields = ["owner__email", "owner", "primary_repo", "secondary_repo", "slug", "name"]
