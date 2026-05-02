from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.urls import reverse

from accounts.models import UserProfile
from listings.models import Listing


class HomeZappCISmokeTests(TestCase):

    def setUp(self):
        self.seller_group, _ = Group.objects.get_or_create(name="Seller")

        self.seller = User.objects.create_user(
            username="seller@test.com",
            email="seller@test.com",
            password="testpass123"
        )
        self.seller.groups.add(self.seller_group)

        UserProfile.objects.update_or_create(
            user=self.seller,
            defaults={
                "role": "Seller",
                "seller_approved": True,
                "seller_request_pending": False,
            }
        )

    def test_homepage_loads(self):
        response = self.client.get(reverse("homepage"))

        self.assertEqual(response.status_code, 200)

    def test_approved_listing_shows_on_homepage(self):
        Listing.objects.create(
            seller=self.seller,
            title="Modern Test House",
            price=250000,
            location="Starkville, MS",
            style="Modern",
            description="A test listing.",
            bedrooms=3,
            bathrooms=2,
            square_footage=1800,
            is_active=True,
            is_sold=False,
            is_approved=True,
            approval_pending=False
        )

        response = self.client.get(reverse("homepage"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Modern Test House")

    def test_pending_listing_does_not_show_on_homepage(self):
        Listing.objects.create(
            seller=self.seller,
            title="Pending Test House",
            price=200000,
            location="Meridian, MS",
            style="Colonial",
            description="A pending listing.",
            bedrooms=3,
            bathrooms=2,
            square_footage=1600,
            is_active=True,
            is_sold=False,
            is_approved=False,
            approval_pending=True
        )

        response = self.client.get(reverse("homepage"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Pending Test House")