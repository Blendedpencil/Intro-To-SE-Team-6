from django.test import TestCase
from django.contrib.auth.models import User


from listings.models import SavedListing
from tests.factories import seed_basic_users, create_listing_for_seller




class WishlistFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        seed_basic_users()
        cls.buyer = User.objects.get(username="buyer0@gmail.com")
        cls.seller = User.objects.get(username="seller0@gmail.com")
        cls.listing = create_listing_for_seller(
            cls.seller,
            title="Wishlist House",
            is_approved=True,
            approval_pending=False,
        )


    def test_buyer_can_wishlist_listing(self):
        self.client.login(username=self.buyer.username, password="test")


        response = self.client.post(f"/listings/save/{self.listing.id}/")
        self.assertEqual(response.status_code, 302)


        self.assertTrue(
            SavedListing.objects.filter(buyer=self.buyer, listing=self.listing).exists()
        )


    def test_buyer_cannot_wishlist_same_listing_twice(self):
        SavedListing.objects.create(buyer=self.buyer, listing=self.listing)


        self.client.login(username=self.buyer.username, password="test")
        response = self.client.post(f"/listings/save/{self.listing.id}/")
        self.assertEqual(response.status_code, 302)


        self.assertEqual(
            SavedListing.objects.filter(buyer=self.buyer, listing=self.listing).count(),
            1
        )


    def test_buyer_can_remove_saved_listing(self):
        SavedListing.objects.create(buyer=self.buyer, listing=self.listing)


        self.client.login(username=self.buyer.username, password="test")
        response = self.client.post(f"/listings/remove-saved/{self.listing.id}/")
        self.assertEqual(response.status_code, 302)


        self.assertFalse(
            SavedListing.objects.filter(buyer=self.buyer, listing=self.listing).exists()
        )
