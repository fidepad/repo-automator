from django.contrib import admin

from automate.models import Project


class ProjectAdmin(admin.ModelAdmin):
    """Project Admin Model."""

    list_display = ["owner", "primary_repo", "secondary_repo"]


admin.site.register(Project, ProjectAdmin)