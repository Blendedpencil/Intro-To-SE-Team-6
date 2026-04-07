from django.test import TestCase
from django.contrib.auth.models import User
from tests.factories import seed_basic_users, create_listing_for_seller
from interactions.models import BuyerApplication
from tests.utils import payment_payload


class PaymentFlowTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        seed_basic_users()

    def test_payment(self):
        buyer = User.objects.get(username="buyer0@gmail.com")
        seller = User.objects.get(username="seller0@gmail.com")

        listing = create_listing_for_seller(seller)

        app = BuyerApplication.objects.create(
            buyer=buyer,
            seller=seller,
            listing=listing,
            first_name="Test",
            last_name="User",
            email="test@gmail.com",
            status="AcceptedBySeller"
        )

        self.client.login(username=buyer.username, password="test")

        response = self.client.post(
            f"/interactions/payment/{app.id}/",
            payment_payload()
        )

        self.assertEqual(response.status_code, 302)