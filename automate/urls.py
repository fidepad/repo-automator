from rest_framework.routers import SimpleRouter

from automate.views import ProjectViewSets

app_name = "repository"

router = SimpleRouter()
router.register("", ProjectViewSets)

urlpatterns = []

urlpatterns += router.urls
