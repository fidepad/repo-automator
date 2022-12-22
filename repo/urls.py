"""repo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

# fmt: off
from drf_spectacular.views import (SpectacularAPIView, SpectacularRedocView,
                                   SpectacularSwaggerView)
from knox import views as knox_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("projects/", include("automate.urls")),

    # Documentation Endpoints
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(), name="swagger"),
    path("redoc/", SpectacularRedocView.as_view(), name="redoc"),

    # Knox Endpoints
    path("auth/login/", knox_views.LoginView.as_view(), name="login"),
    path(r"auth/logout/", knox_views.LogoutView.as_view(), name="logout"),
    path(r"auth/logoutall/", knox_views.LogoutAllView.as_view(), name="logoutall"),
]
