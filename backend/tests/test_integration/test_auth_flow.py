from django.test import TestCase
from tests.factories import seed_basic_users


class AuthFlowTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        seed_basic_users()

    def test_login_redirects(self):
        response = self.client.post("/accounts/login/", {
            "email": "buyer0@gmail.com",
            "password": "test"
        })

        self.assertEqual(response.status_code, 302)