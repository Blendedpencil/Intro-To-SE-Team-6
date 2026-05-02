from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group

from accounts.models import UserProfile, UserReview
from tests.factories import (
    PASSWORD,
    create_buyer,
    create_seller,
    create_admin,
    create_pending_seller,
    login_with_session,
    fake_png,
    fake_txt,
)


class AccountsSection3Tests(TestCase):

    def test_register_user_with_role(self):
        response = self.client.post(reverse("registerPage"), {
            "email": "newbuyer@test.com",
            "password": PASSWORD,
            "profile_picture": fake_png(),
        })

        self.assertEqual(response.status_code, 200)
        user = User.objects.get(username="newbuyer@test.com")
        self.assertTrue(user.check_password(PASSWORD))
        self.assertTrue(user.groups.filter(name="Buyer").exists())

        profile = UserProfile.objects.get(user=user)
        self.assertEqual(profile.role, "Buyer")

    def test_duplicate_buyer_registration_rejected(self):
        create_buyer("duplicate@test.com")

        response = self.client.post(reverse("registerPage"), {
            "email": "duplicate@test.com",
            "password": PASSWORD,
            "profile_picture": fake_png(),
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username="duplicate@test.com").count(), 1)
        self.assertContains(response, "already", status_code=200)

    def test_password_is_hashed(self):
        user = create_buyer("hash@test.com")

        self.assertNotEqual(user.password, PASSWORD)
        self.assertTrue(user.check_password(PASSWORD))

    def test_login_redirects(self):
        buyer = create_buyer("loginbuyer@test.com")

        response = self.client.post(reverse("loginPage"), {
            "email": buyer.username,
            "password": PASSWORD,
        })

        self.assertEqual(response.status_code, 302)

    def test_invalid_login(self):
        response = self.client.post(reverse("loginPage"), {
            "email": "missing@test.com",
            "password": "wrongpassword",
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid")

    def test_buyer_redirect(self):
        buyer = create_buyer("buyerredirect@test.com")
        login_with_session(self.client, buyer)

        response = self.client.get(reverse("dashboard_redirect"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/listings/buyer", response.url)

    def test_seller_redirect(self):
        seller = create_seller("sellerredirect@test.com")
        login_with_session(self.client, seller)

        response = self.client.get(reverse("dashboard_redirect"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/listings/seller", response.url)

    def test_admin_redirect(self):
        admin = create_admin("adminredirect@test.com")
        login_with_session(self.client, admin)

        response = self.client.get(reverse("dashboard_redirect"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin", response.url)

    def test_session_created_on_login(self):
        buyer = create_buyer("sessionbuyer@test.com")

        self.client.post(reverse("loginPage"), {
            "email": buyer.username,
            "password": PASSWORD,
        })

        self.assertIn("bearer_token", self.client.session)
        self.assertIn("bearer_email", self.client.session)

    def test_seller_registration_creates_pending_account(self):
        response = self.client.post(reverse("seller_register_page"), {
            "email": "pendingseller@test.com",
            "password": PASSWORD,
            "profile_picture": fake_png(),
        })

        self.assertEqual(response.status_code, 200)

        user = User.objects.get(username="pendingseller@test.com")
        profile = UserProfile.objects.get(user=user)

        self.assertFalse(user.is_active)
        self.assertEqual(profile.role, "Seller")
        self.assertFalse(profile.seller_approved)
        self.assertTrue(profile.seller_request_pending)

    def test_unapproved_seller_cannot_login(self):
        seller = create_pending_seller("unapprovedseller@test.com")

        response = self.client.post(reverse("seller_login_page"), {
            "email": seller.username,
            "password": PASSWORD,
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "approval")

    def test_buyer_can_update_profile(self):
        buyer = create_buyer("profilebuyer@test.com")
        login_with_session(self.client, buyer)

        response = self.client.post(reverse("buyer_manageprofile"), {
            "first_name": "New",
            "last_name": "Buyer",
            "email": "newprofilebuyer@test.com",
        })

        self.assertEqual(response.status_code, 200)

        buyer.refresh_from_db()
        self.assertEqual(buyer.first_name, "New")
        self.assertEqual(buyer.last_name, "Buyer")
        self.assertEqual(buyer.username, "newprofilebuyer@test.com")

    def test_seller_can_update_profile(self):
        seller = create_seller("profileseller@test.com")
        login_with_session(self.client, seller)

        response = self.client.post(reverse("seller_manage_profile"), {
            "name": "New Seller",
            "email": "newprofileseller@test.com",
            "phone": "555-555-5555",
            "bio": "Updated bio",
        })

        self.assertEqual(response.status_code, 200)

        seller.refresh_from_db()
        profile = UserProfile.objects.get(user=seller)

        self.assertEqual(seller.username, "newprofileseller@test.com")
        self.assertEqual(profile.phone, "555-555-5555")
        self.assertEqual(profile.bio, "Updated bio")

    def test_seller_profile_requires_required_fields(self):
        seller = create_seller("requiredseller@test.com")
        login_with_session(self.client, seller)

        response = self.client.post(reverse("seller_manage_profile"), {
            "name": "",
            "email": "",
            "phone": "",
            "bio": "Missing fields",
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "required")

    def test_logged_out_user_cannot_access_buyer_profile(self):
        response = self.client.get(reverse("buyer_manageprofile"))

        self.assertEqual(response.status_code, 302)

    def test_logged_out_user_cannot_access_seller_profile(self):
        response = self.client.get(reverse("seller_manage_profile"))

        self.assertEqual(response.status_code, 302)

    def test_profile_rejects_invalid_email_format(self):
        buyer = create_buyer("invalidformat@test.com")
        other = create_buyer("usedemail@test.com")
        login_with_session(self.client, buyer)

        response = self.client.post(reverse("buyer_manageprofile"), {
            "first_name": "Bad",
            "last_name": "Email",
            "email": other.username,
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already")

    def test_profile_picture_file_type_validation(self):
        response = self.client.post(reverse("registerPage"), {
            "email": "badpic@test.com",
            "password": PASSWORD,
            "profile_picture": fake_txt(),
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="badpic@test.com").exists())
        self.assertContains(response, "PNG")

    def test_register_rejects_invalid_profile_picture(self):
        response = self.client.post(reverse("seller_register_page"), {
            "email": "badsellerpic@test.com",
            "password": PASSWORD,
            "profile_picture": fake_txt(),
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="badsellerpic@test.com").exists())
        self.assertContains(response, "PNG")

    def test_public_profile_page_loads(self):
        seller = create_seller("publicseller@test.com")

        response = self.client.get(reverse("public_profile", args=[seller.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, seller.username)

    def test_user_can_review_profile(self):
        buyer = create_buyer("reviewer@test.com")
        seller = create_seller("reviewed@test.com")
        login_with_session(self.client, buyer)

        response = self.client.post(reverse("public_profile", args=[seller.id]), {
            "vote": "up"
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            UserReview.objects.filter(
                reviewer=buyer,
                reviewed_user=seller,
                vote=UserReview.THUMBS_UP
            ).exists()
        )

    def test_profile_review_saved_to_database(self):
        buyer = create_buyer("reviewsaved@test.com")
        seller = create_seller("profilesaved@test.com")
        login_with_session(self.client, buyer)

        self.client.post(reverse("public_profile", args=[seller.id]), {
            "vote": "down"
        })

        self.assertEqual(UserReview.objects.count(), 1)

    def test_user_cannot_review_self(self):
        buyer = create_buyer("selfreview@test.com")
        login_with_session(self.client, buyer)

        response = self.client.post(reverse("public_profile", args=[buyer.id]), {
            "vote": "up"
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(UserReview.objects.filter(reviewer=buyer, reviewed_user=buyer).exists())