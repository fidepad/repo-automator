from django.urls import path
from rest_framework.routers import SimpleRouter

from automate.views import WebHookListView, RepositoryViewSets

router = SimpleRouter()
router.register("", RepositoryViewSets)

urlpatterns = [
    path("webhook/", WebHookListView.as_view(), name="webhook")
]

urlpatterns += router.urls
