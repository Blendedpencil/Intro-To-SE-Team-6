from django.test import TestCase
from django.contrib.auth.models import User
from accounts.models import UserProfile
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
    
    class RegistrationTests(TestCase):
        
        @classmethod
        def setUpTestData(cls):
            seed_basic_users()


        def test_duplicate_buyer_registration_rejected(self):
            response = self.client.post("/accounts/register/", {
            "email": "buyer0@gmail.com",
            "password": "test",
        })


            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "already exists")


        def test_seller_registration_creates_pending_account(self):
            response = self.client.post("/accounts/seller/register/", {
                "email": "newseller@gmail.com",
                "password": "test",
        })


            self.assertEqual(response.status_code, 200)


            user = User.objects.get(username="newseller@gmail.com")
            profile = UserProfile.objects.get(user=user)


            self.assertFalse(user.is_active)
            self.assertFalse(profile.seller_approved)
            self.assertTrue(profile.seller_request_pending)
