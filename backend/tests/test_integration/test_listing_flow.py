from django.test import TestCase
from django.contrib.auth.models import User
from listings.models import Listing
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
        
        def test_pending_listing_not_visible_to_buyer(self):
            seller = User.objects.get(username="seller0@gmail.com")
            buyer = User.objects.get(username="buyer0@gmail.com")


            listing = Listing.objects.create(
                seller=seller,
                title="Hidden Pending House",
                price=250000,
                location="Hidden Lane",
                style="Modern",
                description="Pending listing",
                bedrooms=3,
                bathrooms=2,
                square_footage=1500,
                is_active=True,
                is_sold=False,
                is_approved=False,
                approval_pending=True,
            )


            self.client.login(username=buyer.username, password="test")
            response = self.client.get("/listings/buyer/")
            self.assertEqual(response.status_code, 200)
            self.assertNotContains(response, "Hidden Pending House")
