from django.urls import path
from knox.views import LogoutAllView, LogoutView

from repo.api.views import RepoLoginView, RepoRegisterView

urlpatterns = [
    path("auth/login/", RepoLoginView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/logoutall/", LogoutAllView.as_view(), name="logoutall"),
    path("auth/register/", RepoRegisterView.as_view(), name="register"),
]
