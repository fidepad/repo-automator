from rest_framework.routers import SimpleRouter
from django.urls import path, include
from automate.views import ProjectViewSets

app_name = "repository"

router = SimpleRouter()
router.register("", ProjectViewSets)

urlpatterns = [
    path('', include(router.urls))
]
