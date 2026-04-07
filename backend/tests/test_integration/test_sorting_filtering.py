from django.test import TestCase
from django.contrib.auth.models import User, Group


from accounts.models import UserProfile
from interactions.models import BuyerApplication, Notification
from tests.factories import seed_basic_users, create_listing_for_seller




class SellerRejectionFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        seed_basic_users()
        cls.seller = User.objects.get(username="seller0@gmail.com")
        cls.buyer = User.objects.get(username="buyer0@gmail.com")
        cls.admin = User.objects.get(username="admin0@gmail.com")


        cls.listing = create_listing_for_seller(
            seller=cls.seller,
            title="Reject Test House",
            price=350000,
            location="Reject Lane",
            style="Modern",
            description="House for rejection test",
            is_approved=True,
            approval_pending=False,
        )


    def test_seller_rejects_buyer_application(self):
        application = BuyerApplication.objects.create(
            buyer=self.buyer,
            seller=self.seller,
            listing=self.listing,
            first_name="Buyer",
            last_name="Zero",
            email="buyer0@gmail.com",
            status="Pending",
        )


        self.client.login(username=self.seller.username, password="test")


        response = self.client.post(
            f"/listings/seller/negotiation/?application_id={application.id}",
            {"action": "reject"}
        )
        self.assertEqual(response.status_code, 302)


        application.refresh_from_db()
        self.assertEqual(application.status, "RejectedBySeller")


        self.assertTrue(
            Notification.objects.filter(
                recipient=self.buyer,
                title="Application Rejected"
            ).exists()
        )


    def test_admin_rejects_seller_request(self):
        pending_seller = User.objects.create_user(
            username="pendingseller@gmail.com",
            email="pendingseller@gmail.com",
            password="test",
            is_active=False
        )


        seller_group, _ = Group.objects.get_or_create(name="Seller")
        pending_seller.groups.add(seller_group)


        UserProfile.objects.create(
            user=pending_seller,
            role="Seller",
            login_status=False,
            seller_approved=False,
            seller_request_pending=True,
        )


        self.client.login(username=self.admin.username, password="test")
        session = self.client.session
        session["bearer_token"] = "admin-session"
        session["bearer_email"] = self.admin.username
        session.save()


        response = self.client.post(f"/adminpanel/reject-seller/{pending_seller.id}/")
        self.assertEqual(response.status_code, 302)


        self.assertFalse(
            User.objects.filter(username="pendingseller@gmail.com").exists()
        )


    def test_rejected_seller_cannot_log_in(self):
        pending_seller = User.objects.create_user(
            username="rejectlogin@gmail.com",
            email="rejectlogin@gmail.com",
            password="test",
            is_active=False
        )


        seller_group, _ = Group.objects.get_or_create(name="Seller")
        pending_seller.groups.add(seller_group)


        UserProfile.objects.create(
            user=pending_seller,
            role="Seller",
            login_status=False,
            seller_approved=False,
            seller_request_pending=True,
        )


        self.client.login(username=self.admin.username, password="test")
        session = self.client.session
        session["bearer_token"] = "admin-session"
        session["bearer_email"] = self.admin.username
        session.save()


        self.client.post(f"/adminpanel/reject-seller/{pending_seller.id}/")
        self.client.logout()


        response = self.client.post("/accounts/seller/login/", {
            "email": "rejectlogin@gmail.com",
            "password": "test",
        })


        self.assertEqual(response.status_code, 200)
