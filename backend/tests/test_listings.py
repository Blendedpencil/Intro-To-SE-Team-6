from django.test import TestCase
from django.urls import reverse

from listings.models import Listing, SavedListing
from interactions.models import Notification
from tests.factories import (
    PASSWORD,
    create_buyer,
    create_seller,
    create_admin,
    create_approved_listing,
    create_pending_listing,
    create_deleted_listing,
    create_saved_listing,
    login_with_session,
    fake_png,
    fake_txt,
)


class ListingsSection3Tests(TestCase):

    def setUp(self):
        self.buyer = create_buyer("listingbuyer@test.com")
        self.seller = create_seller("listingseller@test.com")
        self.admin = create_admin("listingadmin@test.com")

    def test_homepage_filter_by_location(self):
        create_approved_listing(self.seller, title="Starkville House")
        create_approved_listing(
            self.seller,
            title="Meridian House"
        ).__class__.objects.filter(title="Meridian House").update(location="Meridian, MS")

        response = self.client.get(reverse("homepage"), {"location": "Starkville"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Starkville House")

    def test_homepage_filter_by_style(self):
        create_approved_listing(self.seller, title="Modern House")
        Listing.objects.create(
            seller=self.seller,
            title="Colonial House",
            price=150000,
            location="Meridian, MS",
            style="Colonial",
            description="Colonial test",
            bedrooms=3,
            bathrooms=2,
            square_footage=1500,
            is_active=True,
            is_sold=False,
            is_approved=True,
            approval_pending=False
        )

        response = self.client.get(reverse("homepage"), {"style": "Modern"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Modern House")

    def test_homepage_filter_by_min_price(self):
        create_approved_listing(self.seller, title="Expensive House")
        Listing.objects.create(
            seller=self.seller,
            title="Cheap House",
            price=50000,
            location="Meridian, MS",
            style="Modern",
            description="Cheap test",
            bedrooms=2,
            bathrooms=1,
            square_footage=900,
            is_active=True,
            is_sold=False,
            is_approved=True,
            approval_pending=False
        )

        response = self.client.get(reverse("homepage"), {"min_price": "100000"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Expensive House")

    def test_pending_listing_not_visible_to_buyer(self):
        create_pending_listing(self.seller, title="Pending Hidden House")

        response = self.client.get(reverse("homepage"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Pending Hidden House")

    def test_removed_listing_not_visible_to_buyers(self):
        create_deleted_listing(self.seller, title="Deleted Hidden House")

        response = self.client.get(reverse("homepage"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Deleted Hidden House")

    def test_buyer_can_view_approved_listing_details(self):
        listing = create_approved_listing(self.seller)

        response = self.client.get(reverse("listing_details", args=[listing.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, listing.title)

    def test_user_can_add_to_wishlist(self):
        listing = create_approved_listing(self.seller)
        login_with_session(self.client, self.buyer)

        response = self.client.post(reverse("save_listing", args=[listing.id]))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            SavedListing.objects.filter(buyer=self.buyer, listing=listing).exists()
        )

    def test_save_listing_to_wishlist(self):
        listing = create_approved_listing(self.seller)
        create_saved_listing(self.buyer, listing)

        self.assertTrue(
            SavedListing.objects.filter(buyer=self.buyer, listing=listing).exists()
        )

    def test_wishlist_persists_per_users(self):
        listing = create_approved_listing(self.seller)
        other_buyer = create_buyer("otherwishlist@test.com")

        create_saved_listing(self.buyer, listing)

        self.assertTrue(SavedListing.objects.filter(buyer=self.buyer, listing=listing).exists())
        self.assertFalse(SavedListing.objects.filter(buyer=other_buyer, listing=listing).exists())

    def test_wishlist_page_loads(self):
        listing = create_approved_listing(self.seller)
        create_saved_listing(self.buyer, listing)
        login_with_session(self.client, self.buyer)

        response = self.client.get(reverse("wishlist_page"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, listing.title)

    def test_cannot_duplicate_wishlist_entry(self):
        listing = create_approved_listing(self.seller)
        create_saved_listing(self.buyer, listing)
        login_with_session(self.client, self.buyer)

        self.client.post(reverse("save_listing", args=[listing.id]))

        self.assertEqual(
            SavedListing.objects.filter(buyer=self.buyer, listing=listing).count(),
            1
        )

    def test_create_listing(self):
        login_with_session(self.client, self.seller)

        response = self.client.post(reverse("create_listing"), {
            "title": "Created Listing",
            "price": "300000",
            "location": "Starkville, MS",
            "style": "Modern",
            "description": "Created through test",
            "bedrooms": "3",
            "bathrooms": "2",
            "square_footage": "1800",
            "image": fake_png(),
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Listing.objects.filter(title="Created Listing").exists())

    def test_listing_requires_required_fields(self):
        login_with_session(self.client, self.seller)

        response = self.client.post(reverse("create_listing"), {
            "title": "",
            "price": "",
            "location": "",
            "style": "",
            "description": "",
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Listing.objects.filter(title="").exists())

    def test_listing_shows_pending_status_after_submission(self):
        login_with_session(self.client, self.seller)

        self.client.post(reverse("create_listing"), {
            "title": "Pending Created Listing",
            "price": "300000",
            "location": "Starkville, MS",
            "style": "Modern",
            "description": "Pending after creation",
            "bedrooms": "3",
            "bathrooms": "2",
            "square_footage": "1800",
            "image": fake_png(),
        })

        listing = Listing.objects.get(title="Pending Created Listing")

        self.assertFalse(listing.is_approved)
        self.assertTrue(listing.approval_pending)

    def test_file_upload_validation(self):
        login_with_session(self.client, self.seller)

        response = self.client.post(reverse("create_listing"), {
            "title": "Bad Image Listing",
            "price": "300000",
            "location": "Starkville, MS",
            "style": "Modern",
            "description": "Bad file",
            "bedrooms": "3",
            "bathrooms": "2",
            "square_footage": "1800",
            "image": fake_txt(),
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Listing.objects.filter(title="Bad Image Listing").exists())

    def test_listing_rejects_negative_numbers(self):
        login_with_session(self.client, self.seller)

        response = self.client.post(reverse("create_listing"), {
            "title": "Negative Listing",
            "price": "300000",
            "location": "Starkville, MS",
            "style": "Modern",
            "description": "Negative values",
            "bedrooms": "-1",
            "bathrooms": "2",
            "square_footage": "1800",
            "image": fake_png(),
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Listing.objects.filter(title="Negative Listing").exists())

    def test_seller_can_edit_listing(self):
        listing = create_approved_listing(self.seller)
        login_with_session(self.client, self.seller)

        response = self.client.post(
            reverse("seller_edit_listing") + f"?listing_id={listing.id}",
            {
                "title": "Edited Listing",
                "price": "275000",
                "location": "Meridian, MS",
                "style": "Modern",
                "bedrooms": "4",
                "bathrooms": "3",
                "square_footage": "2000",
                "description": "Edited description",
            }
        )

        listing.refresh_from_db()

        self.assertIn(response.status_code, [200, 302])
        self.assertEqual(listing.title, "Edited Listing")

    def test_seller_cannot_edit_other_seller_listing(self):
        other_seller = create_seller("otherseller@test.com")
        listing = create_approved_listing(other_seller)
        login_with_session(self.client, self.seller)

        response = self.client.post(
            reverse("seller_edit_listing") + f"?listing_id={listing.id}",
            {
                "title": "Bad Edit",
                "price": "1",
                "location": "Nowhere",
                "style": "Modern",
                "bedrooms": "1",
                "bathrooms": "1",
                "square_footage": "1",
                "description": "Should not edit",
            }
        )

        listing.refresh_from_db()

        self.assertNotEqual(listing.title, "Bad Edit")
        self.assertIn(response.status_code, [302, 403, 404])

    def test_latest_listings_rss_loads(self):
        create_approved_listing(self.seller, title="RSS House")

        response = self.client.get(reverse("latest_listings_rss"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("application/rss+xml", response["Content-Type"])
        self.assertContains(response, "RSS House")

    def test_rss_only_shows_public_listings(self):
        create_approved_listing(self.seller, title="Public RSS House")
        create_pending_listing(self.seller, title="Pending RSS House")
        create_deleted_listing(self.seller, title="Deleted RSS House")

        response = self.client.get(reverse("latest_listings_rss"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Public RSS House")
        self.assertNotContains(response, "Pending RSS House")
        self.assertNotContains(response, "Deleted RSS House")