from django.test import TestCase
from django.contrib.auth.models import User
from tests.factories import seed_basic_users, create_pending_listing


class ListingFlowTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        seed_basic_users()

    def test_admin_approves_listing(self):
        seller = User.objects.get(username="seller0@gmail.com")
        admin = User.objects.get(username="admin0@gmail.com")

        listing = create_pending_listing(seller)

        self.client.login(username=admin.username, password="test")

        response = self.client.post(f"/adminpanel/approve-listing/{listing.id}/")

        self.assertEqual(response.status_code, 302)