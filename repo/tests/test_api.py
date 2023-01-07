from rest_framework.reverse import reverse

from accounts.factories import UserFactory
from repo.testing.api import BaseAPITestCase


class RepoLoginViewAPITest(BaseAPITestCase):
    def test_generate_token(self):
        """Assert generating token"""
        user = UserFactory()
        url = reverse("login")
        data = {"email": user.email, "password": "pass"}
        response = self.client.post(url, data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data["user"]["email"], user.email)
        self.assertIn("token", response.data)

        with self.subTest("Invalid credential"):
            data = {"email": user.email, "password": "22"}
            response = self.client.post(url, data)
            self.assertEquals(response.status_code, 400)
            self.assertEquals(
                str(response.data["non_field_errors"][0]), "Invalid login credentials."
            )
