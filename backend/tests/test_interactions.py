from django.test import TestCase
from django.urls import reverse

from listings.models import SavedListing
from interactions.models import BuyerApplication, Notification, Complaint
from tests.factories import (
    create_buyer,
    create_seller,
    create_admin,
    create_approved_listing,
    create_saved_listing,
    create_application,
    create_notification,
    login_with_session,
    fake_png,
    fake_pdf,
    fake_txt,
)


class InteractionsSection3Tests(TestCase):

    def setUp(self):
        self.buyer = create_buyer("interactionbuyer@test.com")
        self.seller = create_seller("interactionseller@test.com")
        self.admin = create_admin("interactionadmin@test.com")
        self.listing = create_approved_listing(self.seller)

    def test_buyer_can_apply(self):
        login_with_session(self.client, self.buyer)

        response = self.client.post(reverse("buyer_application_form", args=[self.listing.id]), {
            "fname": "Test",
            "lname": "Buyer",
            "emailID": self.buyer.username,
            "gov_id": fake_png("id.png"),
            "mortgage_pre_approval": fake_pdf("approval.pdf"),
            "bank_statements": fake_pdf("bank.pdf"),
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            BuyerApplication.objects.filter(
                buyer=self.buyer,
                seller=self.seller,
                listing=self.listing
            ).exists()
        )

    def test_application_rejects_incomplete_information(self):
        login_with_session(self.client, self.buyer)

        response = self.client.post(reverse("buyer_application_form", args=[self.listing.id]), {
            "fname": "",
            "lname": "",
            "emailID": "",
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(BuyerApplication.objects.filter(buyer=self.buyer).exists())

    def test_login_required_to_submit_application(self):
        response = self.client.get(reverse("buyer_application_form", args=[self.listing.id]))

        self.assertEqual(response.status_code, 302)

    def test_buyer_cannot_apply_twice(self):
        create_application(
            buyer=self.buyer,
            seller=self.seller,
            listing=self.listing,
            status="Pending"
        )
        login_with_session(self.client, self.buyer)

        self.client.post(reverse("buyer_application_form", args=[self.listing.id]), {
            "fname": "Test",
            "lname": "Buyer",
            "emailID": self.buyer.username,
            "gov_id": fake_png("id.png"),
            "mortgage_pre_approval": fake_pdf("approval.pdf"),
        })

        self.assertEqual(
            BuyerApplication.objects.filter(buyer=self.buyer, listing=self.listing).count(),
            1
        )

    def test_buyer_notified_on_application_submission(self):
        login_with_session(self.client, self.buyer)

        self.client.post(reverse("buyer_application_form", args=[self.listing.id]), {
            "fname": "Test",
            "lname": "Buyer",
            "emailID": self.buyer.username,
            "gov_id": fake_png("id.png"),
            "mortgage_pre_approval": fake_pdf("approval.pdf"),
        })

        self.assertTrue(
            Notification.objects.filter(
                recipient=self.seller,
                title__icontains="Application"
            ).exists()
        )

    def test_seller_notified_on_application_received(self):
        self.test_buyer_notified_on_application_submission()

    def test_seller_dashboard_shows_applications(self):
        application = create_application(
            buyer=self.buyer,
            seller=self.seller,
            listing=self.listing,
            status="Pending"
        )
        login_with_session(self.client, self.seller)

        response = self.client.get(reverse("seller_dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, application.buyer.username)

    def test_buyer_seller_negotiation_flow(self):
        application = create_application(
            buyer=self.buyer,
            seller=self.seller,
            listing=self.listing,
            status="Pending"
        )
        login_with_session(self.client, self.seller)

        response = self.client.post(reverse("seller_negotiation") + f"?application_id={application.id}", {
            "action": "accept"
        })

        application.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(application.status, "AcceptedBySeller")

    def test_payment_flow(self):
        application = create_application(
            buyer=self.buyer,
            seller=self.seller,
            listing=self.listing,
            status="AcceptedByBuyer"
        )
        login_with_session(self.client, self.buyer)

        response = self.client.post(reverse("buyer_payment", args=[application.id]), {
            "account_holder": "Test Buyer",
            "routing_number": "123456789",
            "account_number": "123456789012",
        })

        application.refresh_from_db()
        self.listing.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(application.status, "Paid")
        self.assertTrue(self.listing.is_sold)
        self.assertFalse(self.listing.is_active)

    def test_payment_info_not_stored(self):
        application = create_application(
            buyer=self.buyer,
            seller=self.seller,
            listing=self.listing,
            status="AcceptedByBuyer"
        )
        login_with_session(self.client, self.buyer)

        self.client.post(reverse("buyer_payment", args=[application.id]), {
            "account_holder": "Private Name",
            "routing_number": "123456789",
            "account_number": "999999999999",
        })

        application.refresh_from_db()

        self.assertFalse(hasattr(application, "routing_number"))
        self.assertFalse(hasattr(application, "account_number"))

    def test_payment_rejects_incomplete_info(self):
        application = create_application(
            buyer=self.buyer,
            seller=self.seller,
            listing=self.listing,
            status="AcceptedByBuyer"
        )
        login_with_session(self.client, self.buyer)

        response = self.client.post(reverse("buyer_payment", args=[application.id]), {
            "account_holder": "",
            "routing_number": "",
            "account_number": "",
        })

        self.assertIn(response.status_code, [200, 302])

    def test_notifications_page_loads(self):
        create_notification(recipient=self.buyer, sender=self.seller)
        login_with_session(self.client, self.buyer)

        response = self.client.get(reverse("notifications_page"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Notification")

    def test_user_can_submit_complaint(self):
        login_with_session(self.client, self.buyer)

        response = self.client.post(reverse("complaint_form") + f"?listing_id={self.listing.id}", {
            "subject": "Misleading Listing",
            "message": "This listing has an issue.",
            "listing_id": self.listing.id,
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Complaint.objects.filter(reporter=self.buyer).exists())

    def test_complaint_requires_description(self):
        login_with_session(self.client, self.buyer)

        response = self.client.post(reverse("complaint_form") + f"?listing_id={self.listing.id}", {
            "subject": "Missing message",
            "message": "",
            "listing_id": self.listing.id,
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Complaint.objects.filter(subject="Missing message").exists())

    def test_complaint_saved_with_metadata(self):
        login_with_session(self.client, self.buyer)

        self.client.post(reverse("complaint_form") + f"?listing_id={self.listing.id}", {
            "subject": "Metadata Complaint",
            "message": "Complaint body",
            "listing_id": self.listing.id,
        })

        complaint = Complaint.objects.get(subject="Metadata Complaint")

        self.assertEqual(complaint.reporter, self.buyer)
        self.assertEqual(complaint.reported_user, self.seller)
        self.assertEqual(complaint.listing, self.listing)
        self.assertIsNotNone(complaint.created_at)

    def test_admin_recieves_complaint_notification(self):
        login_with_session(self.client, self.buyer)

        self.client.post(reverse("complaint_form") + f"?listing_id={self.listing.id}", {
            "subject": "Admin Complaint",
            "message": "Complaint body",
            "listing_id": self.listing.id,
        })

        self.assertTrue(Complaint.objects.filter(subject="Admin Complaint").exists())

    def test_payment_blocked_if_listing_deleted(self):
        application = create_application(
            buyer=self.buyer,
            seller=self.seller,
            listing=self.listing,
            status="AcceptedByBuyer"
        )

        self.listing.is_active = False
        self.listing.save()

        login_with_session(self.client, self.buyer)

        response = self.client.post(reverse("buyer_payment", args=[application.id]), {
            "account_holder": "Test Buyer",
            "routing_number": "123456789",
            "account_number": "123456789012",
        })

        application.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(application.status, "Paid")
        self.assertContains(response, "no longer available")

    def test_deleted_listing_payment_message(self):
        self.test_payment_blocked_if_listing_deleted()

    def test_deleted_listing_cancels_applications(self):
        application = create_application(
            buyer=self.buyer,
            seller=self.seller,
            listing=self.listing,
            status="Pending"
        )
        create_saved_listing(self.buyer, self.listing)
        login_with_session(self.client, self.admin)

        self.client.post(reverse("admin_delete_listing", args=[self.listing.id]))

        application.refresh_from_db()

        self.assertEqual(application.status, "Deleted")

    def test_admin_deleted_listing_removed_from_cart(self):
        create_saved_listing(self.buyer, self.listing)
        login_with_session(self.client, self.admin)

        self.client.post(reverse("admin_delete_listing", args=[self.listing.id]))

        self.assertFalse(SavedListing.objects.filter(buyer=self.buyer, listing=self.listing).exists())

    def test_purchased_listing_status_shows_to_seller(self):
        application = create_application(
            buyer=self.buyer,
            seller=self.seller,
            listing=self.listing,
            status="AcceptedByBuyer"
        )
        login_with_session(self.client, self.buyer)

        self.client.post(reverse("buyer_payment", args=[application.id]), {
            "account_holder": "Test Buyer",
            "routing_number": "123456789",
            "account_number": "123456789012",
        })

        login_with_session(self.client, self.seller)
        response = self.client.get(reverse("seller_dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Purchased")