from knox.models import AuthToken
from knox.settings import knox_settings
from rest_framework.test import APIClient, APITestCase

from accounts.factories import UserFactory
from repo.testing.model import BaseModelTestCase


class BaseAPITestCase(BaseModelTestCase, APITestCase):
    """Base test class for API tests.

    This class serves as a base for all API test classes and provides
    common functionality that can be used across all tests, such as helper
    methods for making API requests and assert functions for validating
    the responses.
    """

    headers = {}

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user = UserFactory()
        cls.token = cls.get_token_for_user(cls.user)

    def setUp(self):
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)

        self.unauthenticated_client = APIClient()

    @staticmethod
    def get_token_for_user(user):
        _, token = AuthToken.objects.create(user, knox_settings.TOKEN_TTL)
        return token

    def authenticate_client(self, user):
        """Authenticates the given user and returns an authenticated APIClient object.

        Parameters:
            user (User): The user to authenticate.

        Returns:
            APIClient: An authenticated APIClient object.
        """
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + self.get_token_for_user(user))
        return client
