from django.test import TestCase
from django.contrib.auth.models import User
from tests.factories import seed_basic_users
from accounts.views import is_admin, is_buyer, is_seller


class AccountsUnitTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        seed_basic_users()

    def test_is_admin(self):
        user = User.objects.get(username="admin0@gmail.com")
        self.assertTrue(is_admin(user))

    def test_is_buyer(self):
        user = User.objects.get(username="buyer0@gmail.com")
        self.assertTrue(is_buyer(user))

    def test_is_seller(self):
        user = User.objects.get(username="seller0@gmail.com")
        self.assertTrue(is_seller(user))

    def test_wrong_role(self):
        user = User.objects.get(username="buyer0@gmail.com")
        self.assertFalse(is_admin(user))