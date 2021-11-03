from django.test import TestCase
from model_bakery import baker
from django.core.exceptions import ValidationError

from ..models import User


class UserTests(TestCase):
    def setUp(self) -> None:
        self.user = baker.make(
            User,
            mobile="01010092181",
            name="Ahmed Loay Shahwan",
            email="ahmed@shahwan.me",
        )
        self.user1 = baker.make(User, mobile="01010092182")

    def test_get_short_name(self):
        self.assertEqual(self.user.get_short_name(), "Ahmed")

    def test_get_full_name(self):
        self.assertEqual(self.user.get_full_name(), "Ahmed Loay Shahwan")

    def test_str(self):
        self.assertEqual(str(self.user), "01010092181")

    def test_repr(self):
        # user with name
        self.assertEqual(
            self.user.__repr__(),
            f"<User {self.user.id}: {str(self.user)} - {self.user.name}>",
        )
        # user without name
        self.assertEqual(
            self.user1.__repr__(),
            f"<User {self.user1.id}: {str(self.user1)}>",
        )

    def test_token_created_on_user_creation(self):
        self.assertIsNotNone(self.user.auth_token)


class ManagerTests(TestCase):
    def test_validerror_if_noshop_with_manager(self):
        with self.assertRaises(ValidationError):
            self.user1 = User.objects.create(mobile="01093862820", type=["MANAGER"])
