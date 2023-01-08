from rest_framework.routers import SimpleRouter

from automate.views import ProjectViewSets

app_name = "project"

router = SimpleRouter()
router.register("", ProjectViewSets)

urlpatterns = router.urls
