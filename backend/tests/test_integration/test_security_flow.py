from django.test import TestCase
from django.contrib.auth.models import User


from adminpanel.models import BanRecord
from tests.factories import seed_basic_users




class SecurityFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        seed_basic_users()


    def test_logout_prevents_access_to_buyer_dashboard(self):
        buyer = User.objects.get(username="buyer0@gmail.com")
        self.client.login(username=buyer.username, password="test")


        session = self.client.session
        session["bearer_token"] = "buyer-session"
        session["bearer_email"] = buyer.username
        session.save()


        response = self.client.get("/listings/buyer/")
        self.assertEqual(response.status_code, 200)


        response = self.client.get("/accounts/logout/")
        self.assertEqual(response.status_code, 302)


        response = self.client.get("/listings/buyer/")
        self.assertEqual(response.status_code, 302)


    def test_logout_prevents_access_to_admin_home(self):
        admin = User.objects.get(username="admin0@gmail.com")
        self.client.login(username=admin.username, password="test")


        session = self.client.session
        session["bearer_token"] = "admin-session"
        session["bearer_email"] = admin.username
        session.save()


        response = self.client.get("/adminpanel/home/")
        self.assertEqual(response.status_code, 200)


        response = self.client.get("/accounts/logout/")
        self.assertEqual(response.status_code, 302)


        response = self.client.get("/adminpanel/home/")
        self.assertEqual(response.status_code, 302)


    def test_banned_buyer_cannot_log_in(self):
        admin = User.objects.get(username="admin0@gmail.com")
        buyer = User.objects.get(username="buyer0@gmail.com")


        buyer.is_active = False
        buyer.save()


        BanRecord.objects.create(
            user=buyer,
            banned_by=admin,
            reason="Security test ban"
        )


        response = self.client.post("/accounts/login/", {
            "email": buyer.username,
            "password": "test",
        })


        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid email or password")


    def test_banned_admin_cannot_log_in(self):
        admin = User.objects.get(username="admin1@gmail.com")
        admin.is_active = False
        admin.save()


        response = self.client.post("/adminpanel/login/", {
            "adminEmail": admin.username,
            "adminPass": "test",
        })


        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid email or password")


    def test_logged_out_user_cannot_access_seller_dashboard(self):
        response = self.client.get("/listings/seller/dashboard/")
        self.assertEqual(response.status_code, 302)


    def test_logged_out_user_cannot_access_wishlist(self):
        response = self.client.get("/listings/wishlist/")
        self.assertEqual(response.status_code, 302)
