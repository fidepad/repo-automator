from django.contrib.auth import get_user_model

from repo.testing.model import BaseModelTestCase

User = get_user_model()


class UserTestCase(BaseModelTestCase):
    """Test case for User Model."""

    def test_user_model_manager(self):
        """Test user model custom manager."""
        with self.subTest("Create User"):
            user_email = "a@a.com"
            user = User.objects.create_user(
                email=user_email, name="test user", password="1234"
            )
            self.assertTrue(
                User.objects.filter(email=user_email).exists(),
            )
            self.assertEqual(user.is_admin, False)
            self.assertEqual(user.email, user_email)

        with self.subTest("Create Super User"):
            user_email = "test-2@a.com"
            user = User.objects.create_superuser(
                email=user_email, name="test user", password="1234"
            )
            self.assertTrue(
                User.objects.filter(email=user_email).exists(),
            )
            self.assertEqual(user.is_admin, True)
            self.assertEqual(user.email, user_email)
