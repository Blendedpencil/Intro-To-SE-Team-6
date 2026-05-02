from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from accounts.models import UserProfile
from listings.models import Listing, SavedListing
from interactions.models import Notification, BuyerApplication
from adminpanel.models import BanRecord, ModerationHistory
from tests.factories import (
    PASSWORD,
    create_buyer,
    create_seller,
    create_admin,
    create_pending_seller,
    create_approved_listing,
    create_pending_listing,
    create_application,
    create_saved_listing,
    login_with_session,
)


class AdminPanelSection3Tests(TestCase):

    def setUp(self):
        self.admin = create_admin("adminpanel@test.com")
        self.buyer = create_buyer("adminbuyer@test.com")
        self.seller = create_seller("adminseller@test.com")
        self.listing = create_approved_listing(self.seller)

    def test_admin_login_route_exists(self):
        response = self.client.get(reverse("admin_login_page"))

        self.assertEqual(response.status_code, 200)

    def test_admin_ban_requires_reason(self):
        login_with_session(self.client, self.admin)

        response = self.client.post(reverse("admin_ban_user"), {
            "ban_user": "1",
            "uName": self.buyer.username,
            "banReason": "",
        })

        self.buyer.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.buyer.is_active)

    def test_banned_user_cannot_login(self):
        self.buyer.is_active = False
        self.buyer.save()

        response = self.client.post(reverse("loginPage"), {
            "email": self.buyer.username,
            "password": PASSWORD,
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "banned")

    def test_admin_ban_logs_record(self):
        login_with_session(self.client, self.admin)

        self.client.post(reverse("admin_ban_user"), {
            "ban_user": "1",
            "uName": self.buyer.username,
            "banReason": "Policy violation",
        })

        self.buyer.refresh_from_db()

        self.assertFalse(self.buyer.is_active)
        self.assertTrue(BanRecord.objects.filter(user=self.buyer).exists())
        self.assertTrue(ModerationHistory.objects.filter(target_user=self.buyer).exists())

    def test_banning_seller_removes_active_listings(self):
        login_with_session(self.client, self.admin)

        self.client.post(reverse("admin_ban_user"), {
            "ban_user": "1",
            "uName": self.seller.username,
            "banReason": "Policy violation",
        })

        self.seller.refresh_from_db()

        self.assertFalse(self.seller.is_active)

    def test_user_notified_on_ban_with_reason(self):
        login_with_session(self.client, self.admin)

        self.client.post(reverse("admin_ban_user"), {
            "ban_user": "1",
            "uName": self.buyer.username,
            "banReason": "Policy violation",
        })

        self.assertTrue(BanRecord.objects.filter(user=self.buyer, reason="Policy violation").exists())

    def test_admin_delete_listing(self):
        login_with_session(self.client, self.admin)

        response = self.client.post(reverse("admin_delete_listing", args=[self.listing.id]))

        self.listing.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.listing.is_active)

    def test_admin_delete_listing_logs_action(self):
        login_with_session(self.client, self.admin)

        self.client.post(reverse("admin_delete_listing", args=[self.listing.id]))

        self.assertTrue(
            ModerationHistory.objects.filter(
                target_listing_title=self.listing.title
            ).exists()
        )

    def test_seller_notified_on_listing_removal(self):
        login_with_session(self.client, self.admin)

        self.client.post(reverse("admin_delete_listing", args=[self.listing.id]))

        self.assertTrue(
            Notification.objects.filter(
                recipient=self.seller,
                title__icontains="Deleted"
            ).exists()
        )

    def test_admin_can_view_listing_details(self):
        login_with_session(self.client, self.admin)

        response = self.client.get(reverse("admin_home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.listing.title)

    def test_admin_can_view_listing_details_full(self):
        self.test_admin_can_view_listing_details()

    def test_listing_submission_timestamp_displayed(self):
        login_with_session(self.client, self.admin)
        pending = create_pending_listing(self.seller, title="Timestamp Listing")

        response = self.client.get(reverse("admin_home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Timestamp Listing")
        self.assertIsNotNone(pending.created_at)

    def test_admin_can_approve_listing(self):
        pending = create_pending_listing(self.seller, title="Approve Me")
        login_with_session(self.client, self.admin)

        response = self.client.post(reverse("approve_listing", args=[pending.id]))

        pending.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertTrue(pending.is_approved)
        self.assertFalse(pending.approval_pending)

    def test_seller_notified_on_listing_approval(self):
        pending = create_pending_listing(self.seller, title="Notify Approval")
        login_with_session(self.client, self.admin)

        self.client.post(reverse("approve_listing", args=[pending.id]))

        self.assertTrue(
            Notification.objects.filter(
                recipient=self.seller,
                title__icontains="Approved"
            ).exists()
        )

    def test_seller_notified_on_rejection(self):
        pending = create_pending_listing(self.seller, title="Reject Me")
        login_with_session(self.client, self.admin)

        self.client.post(reverse("reject_listing", args=[pending.id]), {
            "reason": "Missing details"
        })

        pending.refresh_from_db()

        self.assertFalse(pending.is_approved)
        self.assertFalse(pending.approval_pending)
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.seller,
                title__icontains="Rejected"
            ).exists()
        )

    def test_listing_approval_logs_timestamp(self):
        pending = create_pending_listing(self.seller, title="Timestamp Approval")
        login_with_session(self.client, self.admin)

        self.client.post(reverse("approve_listing", args=[pending.id]))

        history = ModerationHistory.objects.filter(
            target_listing_title=pending.title
        ).first()

        self.assertIsNotNone(history)
        self.assertIsNotNone(history.created_at)

    def test_admin_search_user(self):
        login_with_session(self.client, self.admin)

        response = self.client.get(reverse("admin_search_user"), {
            "searchUsers": self.buyer.username
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.buyer.username)

    def test_admin_rejects_seller_request(self):
        pending_seller = create_pending_seller("rejectseller@test.com")
        login_with_session(self.client, self.admin)

        response = self.client.post(reverse("reject_seller_request", args=[pending_seller.id]))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(User.objects.filter(username="rejectseller@test.com").exists())

    def test_seller_registration_creates_pending_account(self):
        pending_seller = create_pending_seller("createdpending@test.com")
        profile = UserProfile.objects.get(user=pending_seller)

        self.assertFalse(pending_seller.is_active)
        self.assertTrue(profile.seller_request_pending)
        self.assertFalse(profile.seller_approved)

    def test_seller_notified_on_review(self):
        pending_seller = create_pending_seller("reviewpending@test.com")
        profile = UserProfile.objects.get(user=pending_seller)

        self.assertTrue(profile.seller_request_pending)

    def test_seller_notified_on_approval(self):
        pending_seller = create_pending_seller("approvepending@test.com")
        login_with_session(self.client, self.admin)

        self.client.post(reverse("approve_seller_request", args=[pending_seller.id]))

        profile = UserProfile.objects.get(user=pending_seller)
        pending_seller.refresh_from_db()

        self.assertTrue(pending_seller.is_active)
        self.assertTrue(profile.seller_approved)
        self.assertFalse(profile.seller_request_pending)