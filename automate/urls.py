from rest_framework.routers import DefaultRouter

from automate.views import ProjectViewSets

app_name = "project"

router = DefaultRouter()
router.register("", ProjectViewSets)

urlpatterns = router.urls
