from django.test import TestCase
from django.contrib.auth.models import User
from tests.factories import seed_basic_users, create_listing_for_seller
from tests.utils import application_payload


class ApplicationFlowTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        seed_basic_users()

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