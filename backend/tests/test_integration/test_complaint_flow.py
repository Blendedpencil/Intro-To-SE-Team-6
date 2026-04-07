from django.test import TestCase
from django.contrib.auth.models import User

from interactions.models import Complaint
from tests.factories import seed_basic_users, create_listing_for_seller


class ComplaintFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        seed_basic_users()
        cls.buyer = User.objects.get(username="buyer0@gmail.com")
        cls.seller = User.objects.get(username="seller0@gmail.com")
        cls.admin = User.objects.get(username="admin0@gmail.com")
        cls.listing = create_listing_for_seller(
            cls.seller,
            title="Complaint House",
            is_approved=True,
            approval_pending=False,
        )

    def test_buyer_can_submit_complaint(self):
        self.client.login(username=self.buyer.username, password="test")

        response = self.client.post("/interactions/complaint/", {
            "listing_id": self.listing.id,
            "subject": "Fraud concern",
            "message": "This listing looks suspicious.",
        })

        self.assertEqual(response.status_code, 200)

        complaint = Complaint.objects.get(listing=self.listing, reporter=self.buyer)
        self.assertEqual(complaint.reported_user, self.seller)
        self.assertEqual(complaint.subject, "Fraud concern")

    def test_complaint_requires_description(self):
        self.client.login(username=self.buyer.username, password="test")

        response = self.client.post("/interactions/complaint/", {
            "listing_id": self.listing.id,
            "subject": "Missing details",
            "message": "",
        })

        self.assertEqual(response.status_code, 200)

    def test_admin_can_view_complaint_from_admin_home(self):
        Complaint.objects.create(
            reporter=self.buyer,
            reported_user=self.seller,
            listing=self.listing,
            subject="Complaint Subject",
            message="Complaint body",
        )

        self.client.login(username=self.admin.username, password="test")
        session = self.client.session
        session["bearer_token"] = "admin-session"
        session.save()

        response = self.client.get("/adminpanel/home/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Complaint House")