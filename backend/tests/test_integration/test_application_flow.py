from django.test import TestCase
from django.contrib.auth.models import User
from unittest import expectedFailure
from tests.factories import seed_basic_users, create_listing_for_seller
from tests.utils import application_payload
from interactions.models import BuyerApplication


class ApplicationFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        seed_basic_users()
        cls.buyer = User.objects.get(username="buyer0@gmail.com")
        cls.seller = User.objects.get(username="seller0@gmail.com")
        cls.listing = create_listing_for_seller(
            cls.seller,
            title="Test House",
            is_approved=True,
            approval_pending=False,
        )


    @expectedFailure
    def test_buyer_cannot_apply_twice_for_same_listing(self):
        self.client.login(username=self.buyer.username, password="test")


        first_response = self.client.post(
            f"/interactions/apply/{self.listing.id}/",
            application_payload()
        )
        self.assertIn(first_response.status_code, [200, 302])


        second_response = self.client.post(
            f"/interactions/apply/{self.listing.id}/",
            application_payload()
        )
        self.assertIn(second_response.status_code, [200, 302])


        self.assertEqual(
            BuyerApplication.objects.filter(
                buyer=self.buyer,
                listing=self.listing
            ).count(),
            1
        )



    def test_application_flow(self):
        buyer = User.objects.get(username="buyer0@gmail.com")
        seller = User.objects.get(username="seller0@gmail.com")

        listing = create_listing_for_seller(seller)

        self.client.login(username=buyer.username, password="test")

        response = self.client.post(
            f"/interactions/apply/{listing.id}/",
            application_payload()
        )

        self.assertEqual(response.status_code, 302)
        
