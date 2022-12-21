import json

from rest_framework import generics, response, status, viewsets

from automate.models import Repository
from automate.serializers import RepositorySerializer


class WebHookListView(generics.GenericAPIView):
    """API View to receive payload from github."""

    def post(self, request):
        """This webhook receives payload from github whenever a PR is approved and merged"""
        content = json.loads(request.body)
        return response.Response(
            {"message": "success", "action": content.get("action")},
            status=status.HTTP_200_OK,
        )


class RepositoryViewSets(viewsets.ModelViewSet):
    """Repository ViewSets."""
    serializer_class = RepositorySerializer
    queryset = Repository.objects.all()

    def get_queryset(self):
        owner = self.request.user
        return Repository.objects.filter(owner=owner)
