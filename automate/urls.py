from rest_framework.routers import SimpleRouter
from django.urls import path, include
from automate.views import ProjectViewSets, WebHookViewSet

app_name = "repository"

router = SimpleRouter()
router.register("", ProjectViewSets)
router.register("webhook/id", WebHookViewSet)

urlpatterns = router.urls
