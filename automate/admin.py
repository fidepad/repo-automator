from django.contrib import admin

from automate.models import Project


class ProjectAdmin(admin.ModelAdmin):
    list_display = ["owner", "primary_repo", "secondary_repo"]


admin.site.register(Project, ProjectAdmin)
