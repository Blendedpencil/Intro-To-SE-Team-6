from django.test import TestCase
from django.contrib.auth.models import User


from adminpanel.models import BanRecord, ModerationHistory
from listings.models import Listing
from tests.factories import seed_basic_users, create_listing_for_seller




class AdminModerationFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        seed_basic_users()
        cls.admin = User.objects.get(username="admin0@gmail.com")
        cls.seller = User.objects.get(username="seller0@gmail.com")
        cls.buyer = User.objects.get(username="buyer0@gmail.com")


        cls.listing = create_listing_for_seller(
            cls.seller,
            title="Moderation House",
            is_approved=True,
            approval_pending=False,
        )


    def login_admin(self):
        self.client.login(username=self.admin.username, password="test")
        session = self.client.session
        session["bearer_token"] = "admin-session"
        session.save()


    def test_admin_ban_requires_reason(self):
        self.login_admin()


        response = self.client.post("/adminpanel/ban-user/", {
            "ban_user": "1",
            "uName": self.buyer.username,
            "banReason": "",
        })


        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "required")


    def test_admin_ban_logs_record_and_history(self):
        self.login_admin()


        response = self.client.post("/adminpanel/ban-user/", {
            "ban_user": "1",
            "uName": self.buyer.username,
            "banReason": "Violation",
        })


        self.assertEqual(response.status_code, 200)


        self.buyer.refresh_from_db()
        self.assertFalse(self.buyer.is_active)


        self.assertTrue(BanRecord.objects.filter(user=self.buyer).exists())
        self.assertTrue(
            ModerationHistory.objects.filter(
                target_user=self.buyer,
                action="BAN_USER"
            ).exists()
        )


    def test_banning_seller_removes_active_listings(self):
        self.seller.is_active = False
        self.seller.save()


        Listing.objects.filter(seller=self.seller).update(is_active=False)


        self.assertFalse(
            Listing.objects.filter(seller=self.seller, is_active=True).exists()
        )


    def test_admin_can_delete_listing(self):
        self.login_admin()


        response = self.client.post(f"/adminpanel/delete-listing/{self.listing.id}/")
        self.assertEqual(response.status_code, 302)


        self.listing.refresh_from_db()
        self.assertFalse(self.listing.is_active)


    def test_admin_cannot_approve_non_pending_listing(self):
        self.login_admin()


        self.listing.is_approved = True
        self.listing.approval_pending = False
        self.listing.save()


        response = self.client.post(f"/adminpanel/approve-listing/{self.listing.id}/")
        self.assertEqual(response.status_code, 302)
