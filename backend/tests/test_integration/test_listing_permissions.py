from django.test import TestCase
from django.contrib.auth.models import User


from tests.factories import seed_basic_users, create_listing_for_seller




class ListingPermissionFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        seed_basic_users()
        cls.seller1 = User.objects.get(username="seller0@gmail.com")
        cls.seller2 = User.objects.get(username="seller1@gmail.com")
        cls.buyer = User.objects.get(username="buyer0@gmail.com")


        cls.listing = create_listing_for_seller(
            cls.seller1,
            title="Owner House",
            is_approved=True,
            approval_pending=False,
        )


    def test_seller_can_edit_own_listing(self):
        self.client.login(username=self.seller1.username, password="test")


        response = self.client.post("/listings/seller/edit/", {
            "listing_id": self.listing.id,
            "title": "Updated Owner House",
            "price": "350000",
            "location": "Updated Lane",
            "style": "Modern",
            "description": "Updated description",
            "bedrooms": 4,
            "bathrooms": 3,
            "square_footage": 2200,
        })


        self.assertEqual(response.status_code, 200)


    def test_seller_cannot_edit_other_seller_listing(self):
        self.client.login(username=self.seller2.username, password="test")


        response = self.client.post("/listings/seller/edit/", {
            "listing_id": self.listing.id,
            "title": "Illegal Edit",
            "price": "999999",
            "location": "Hack Lane",
            "style": "Modern",
            "description": "Should not work",
            "bedrooms": 1,
            "bathrooms": 1,
            "square_footage": 100,
        })


        self.assertIn(response.status_code, [302, 404])


    def test_removed_listing_not_visible_to_buyers(self):
        self.listing.is_active = False
        self.listing.save()


        self.client.login(username=self.buyer.username, password="test")
        response = self.client.get("/listings/buyer/")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Owner House")
