from django.contrib import admin

from automate.models import Repository


class RepositoryAdmin(admin.ModelAdmin):
    list_display = ["owner", "primary_repo", "secondary_repo"]


admin.site.register(Repository, RepositoryAdmin)
