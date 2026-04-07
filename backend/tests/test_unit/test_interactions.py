from django.test import TestCase
from django.contrib.auth.models import User
from tests.factories import seed_basic_users, create_listing_for_seller
from interactions.models import BuyerApplication


class InteractionUnitTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        seed_basic_users()

    def setUp(self):
        self.buyer = User.objects.get(username="buyer0@gmail.com")
        self.seller = User.objects.get(username="seller0@gmail.com")
        self.listing = create_listing_for_seller(self.seller)

    def test_application_creation(self):
        app = BuyerApplication.objects.create(
            buyer=self.buyer,
            seller=self.seller,
            listing=self.listing,
            first_name="Test",
            last_name="User",
            email="test@gmail.com"
        )

        self.assertEqual(app.status, "Pending")