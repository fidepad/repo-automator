from django.contrib import admin

from automate.models import Project


class ProjectAdmin(admin.ModelAdmin):
    """Project Admin Model."""

    list_display = [
        "owner",
        "name",
        "primary_repo_name",
        "secondary_repo_name",
    ]


admin.site.register(Project, ProjectAdmin)
