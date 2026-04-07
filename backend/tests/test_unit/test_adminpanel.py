from django.test import TestCase
from django.contrib.auth.models import User
from tests.factories import seed_basic_users
from adminpanel.models import BanRecord


class AdminPanelUnitTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        seed_basic_users()

    def test_ban_user(self):
        admin = User.objects.get(username="admin0@gmail.com")
        user = User.objects.get(username="buyer0@gmail.com")

        BanRecord.objects.create(
            user=user,
            banned_by=admin,
            reason="Test ban"
        )

        user.is_active = False
        user.save()

        self.assertFalse(user.is_active)