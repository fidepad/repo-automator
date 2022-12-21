from django.urls import path

from automate.views import WebHookListView

urlpatterns = [path("webhook/", WebHookListView.as_view(), name="webhook")]
