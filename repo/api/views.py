from django.contrib.auth import get_user_model
from knox.views import LoginView
from rest_framework.permissions import AllowAny

from repo.api.serializers import AuthTokenSerializer

User = get_user_model()


class RepoLoginView(LoginView):
    """Endpoint used in generating access token for a user"""
    permission_classes = (AllowAny,)
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        # Using `AuthTokenSerializer` for just validation of input field.
        serializer = AuthTokenSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        request.user = serializer.validated_data["user"]
        return super().post(request, *args, **kwargs)
