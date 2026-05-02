from django.test import TestCase, Client
from django.urls import reverse

from accounts.models import UserReview
from listings.models import SavedListing
from interactions.models import BuyerApplication, Notification, Complaint
from tests.factories import (
    create_buyer,
    create_seller,
    create_admin,
    create_approved_listing,
    create_pending_listing,
    create_application,
    create_notification,
    create_saved_listing,
    create_complaint,
    login_with_session,
)


class SecuritySection3Tests(TestCase):

    def setUp(self):
        self.buyer = create_buyer("securitybuyer@test.com")
        self.other_buyer = create_buyer("othersecuritybuyer@test.com")
        self.seller = create_seller("securityseller@test.com")
        self.other_seller = create_seller("othersecurityseller@test.com")
        self.admin = create_admin("securityadmin@test.com")
        self.listing = create_approved_listing(self.seller)

    def test_logged_out_user_cannot_submit_profile_review(self):
        response = self.client.post(reverse("public_profile", args=[self.seller.id]), {
            "vote": "up"
        })

        self.assertEqual(response.status_code, 302)
        self.assertFalse(UserReview.objects.exists())

    def test_user_can_only_update_own_profile_review(self):
        login_with_session(self.client, self.buyer)

        self.client.post(reverse("public_profile", args=[self.seller.id]), {
            "vote": "up"
        })

        login_with_session(self.client, self.other_buyer)

        self.client.post(reverse("public_profile", args=[self.seller.id]), {
            "vote": "down"
        })

        first_review = UserReview.objects.get(
            reviewer=self.buyer,
            reviewed_user=self.seller
        )

        second_review = UserReview.objects.get(
            reviewer=self.other_buyer,
            reviewed_user=self.seller
        )

        self.assertEqual(first_review.vote, UserReview.THUMBS_UP)
        self.assertEqual(second_review.vote, UserReview.THUMBS_DOWN)

    def test_buyer_cannot_access_other_buyer_payment(self):
        application = create_application(
            buyer=self.buyer,
            seller=self.seller,
            listing=self.listing,
            status="AcceptedByBuyer"
        )

        login_with_session(self.client, self.other_buyer)

        response = self.client.get(reverse("buyer_payment", args=[application.id]))

        self.assertIn(response.status_code, [302, 403, 404])

    def test_buyer_cannot_access_other_buyer_application_decision(self):
        application = create_application(
            buyer=self.buyer,
            seller=self.seller,
            listing=self.listing,
            status="AcceptedBySeller"
        )

        login_with_session(self.client, self.other_buyer)

        response = self.client.post(reverse("buyer_application_decision", args=[application.id]), {
            "action": "accept"
        })

        application.refresh_from_db()

        self.assertIn(response.status_code, [302, 403, 404])
        self.assertEqual(application.status, "AcceptedBySeller")

    def test_seller_cannot_access_other_seller_negotiation(self):
        application = create_application(
            buyer=self.buyer,
            seller=self.seller,
            listing=self.listing,
            status="Pending"
        )

        login_with_session(self.client, self.other_seller)

        response = self.client.post(reverse("seller_negotiation") + f"?application_id={application.id}", {
            "action": "accept"
        })

        application.refresh_from_db()

        self.assertIn(response.status_code, [302, 403, 404])
        self.assertEqual(application.status, "Pending")

    def test_user_cannot_modify_other_user_notification(self):
        notification = create_notification(
            recipient=self.buyer,
            sender=self.seller
        )

        login_with_session(self.client, self.other_buyer)

        response = self.client.post(reverse("mark_notification_read", args=[notification.id]))

        notification.refresh_from_db()

        self.assertIn(response.status_code, [302, 403, 404])
        self.assertFalse(notification.is_read)

    def test_csrf_required_for_profile_review(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.login(username=self.buyer.username, password="testpass123")

        session = csrf_client.session
        session["bearer_token"] = "test-token"
        session["bearer_email"] = self.buyer.username
        session.save()

        response = csrf_client.post(reverse("public_profile", args=[self.seller.id]), {
            "vote": "up"
        })

        self.assertEqual(response.status_code, 403)

    def test_csrf_required_for_payment(self):
        application = create_application(
            buyer=self.buyer,
            seller=self.seller,
            listing=self.listing,
            status="AcceptedByBuyer"
        )

        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.login(username=self.buyer.username, password="testpass123")

        session = csrf_client.session
        session["bearer_token"] = "test-token"
        session["bearer_email"] = self.buyer.username
        session.save()

        response = csrf_client.post(reverse("buyer_payment", args=[application.id]), {
            "account_holder": "Test Buyer",
            "routing_number": "123456789",
            "account_number": "123456789012",
        })

        self.assertEqual(response.status_code, 403)

    def test_csrf_required_for_admin_delete_listing(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.login(username=self.admin.username, password="testpass123")

        session = csrf_client.session
        session["bearer_token"] = "test-token"
        session["bearer_email"] = self.admin.username
        session.save()

        response = csrf_client.post(reverse("admin_delete_listing", args=[self.listing.id]))

        self.assertEqual(response.status_code, 403)

    def test_rss_does_not_show_private_data(self):
        application = create_application(
            buyer=self.buyer,
            seller=self.seller,
            listing=self.listing,
            status="Pending"
        )

        create_saved_listing(self.buyer, self.listing)
        create_complaint(self.buyer, self.listing)

        response = self.client.get(reverse("latest_listings_rss"))
        content = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.listing.title, content)
        self.assertNotIn(application.email, content)
        self.assertNotIn("Complaint", content)
        self.assertNotIn("bank", content.lower())
        self.assertNotIn("payment", content.lower())

    def test_seller_decision_cannot_be_changed(self):
        application = create_application(
            buyer=self.buyer,
            seller=self.seller,
            listing=self.listing,
            status="AcceptedBySeller"
        )

        login_with_session(self.client, self.seller)

        self.client.post(reverse("seller_negotiation") + f"?application_id={application.id}", {
            "action": "reject"
        })

        application.refresh_from_db()

        self.assertEqual(application.status, "AcceptedBySeller")