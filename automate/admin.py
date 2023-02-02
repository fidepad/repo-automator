from django.contrib import admin

from .models import History, Project, ProjectActivities


class ProjectAdmin(admin.ModelAdmin):
    """Project Admin Model."""

    list_display = [
        "owner",
        "name",
        "primary_repo_name",
        "secondary_repo_name",
    ]


admin.site.register(Project, ProjectAdmin)
admin.site.register(History)
admin.site.register(ProjectActivities)
