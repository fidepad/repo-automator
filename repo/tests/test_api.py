from rest_framework.reverse import reverse

from accounts.factories import UserFactory
from repo.testing.api import BaseAPITestCase


class RepoLoginViewAPITest(BaseAPITestCase):
    """RepoLoginView Test case."""

    def test_generate_token(self):
        """Assert generating token."""
        user = UserFactory()
        url = reverse("login")
        data = {"email": user.email, "password": "pass"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["user"]["email"], user.email)
        self.assertIn("token", response.data)

        with self.subTest("Invalid credential"):
            data = {"email": user.email, "password": "22"}
            response = self.client.post(url, data)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(
                str(response.data["non_field_errors"][0]), "Invalid login credentials."
            )


class TestRepoRegister(BaseAPITestCase):
    """Test for Register."""

    def setUp(self) -> None:
        self.user = UserFactory()
        self.url = reverse("register")
        self.data = {
            "email": "test@mail.com",
            "name": "Full Name",
            "password": "TestingPassword123.",
            "terms": True
        }

    def test_successful_register(self):
        """This ensures user is registered successfully."""
        response = self.client.post(self.url, self.data)
        content = response.json()
        self.assertTrue(response.status_code == 201)
        self.assertEqual(content["message"], "User created successfully!")

        with self.subTest("Test to ensure user can login in successfully"):
            response = self.client.post(reverse("login"), self.data)

            self.assertTrue(response.status_code == 200)
            self.assertEqual(response.data["user"]["email"], self.data["email"])
            self.assertIn("token", response.data)

    def test_registration_validation(self):
        """This test checks for validation in registration."""

        with self.subTest("This test ensures terms and conditions are agreed upon."):
            self.data["terms"] = False
            response = self.client.post(self.url, self.data)
            content = response.json()
            self.assertTrue(response.status_code == 400)
            self.assertEqual(content["non_field_errors"][0], "Read and accept our terms and conditions!")
        
        with self.subTest("This test ensures existing user can't be re-registered."):
            self.data["email"] = self.user.email
            response = self.client.post(self.url, self.data)
            content = response.json()
            self.assertTrue(response.status_code == 400)
            self.assertEqual(content["email"][0], "user with this email already exists.")
