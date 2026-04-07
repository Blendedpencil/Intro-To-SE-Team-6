#example
from django.test import TestCase

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from rest_framework.authtoken.models import Token

from accounts.models import UserProfile
from adminpanel.models import BanRecord, ModerationHistory
from interactions.models import Complaint, Notification
from listings.models import Listing
from django.contrib.auth.models import User, Group
from PIL import Image

from accounts.views import is_buyer, is_seller, is_admin, login_bearer, register_page, seller_register_page, seller_login_page, admin_create_account, buyer_page, seller_page, admin_page, buyer_manageprofile, seller_manage_profile, logout_bearer, dashboard_redirect

'''
class testCase(TestCase):
    def setUp(self):
        testVar = 5
    def testThing(self):
        self.assertEqual(testVar, 5)

class testCase2(TestCase):
    def setUp(self):
        testVar = 5
    def testThing(self):
        self.assertEqual(testVar, 5)
'''

#accounts
#unit - account creation
class testCreateAccount(TestCase):
    def setUp(self):
        for i in range(5):
            person = 'admin' + str(i)
            person_email = person + '@gmail.com'
            user = User.objects.create_user(
                        username=person_email,
                        email=person_email,
                        password="test",
                        is_active=True
                    )
            group, _ = Group.objects.get_or_create(name="Admin")
            user.groups.add(group)
            UserProfile.objects.create(
                        user=user,
                        role='Admin',
                        login_status=False,
                        seller_approved=False,
                        seller_request_pending=False
                    )
        i = 0
        for i in range(5):
            person = 'buyer' + str(i)
            person_email = person + '@gmail.com'
            user = User.objects.create_user(
                        username=person_email,
                        email=person_email,
                        password="test",
                        is_active=True
                    )
            group, _ = Group.objects.get_or_create(name="Buyer")
            user.groups.add(group)
            UserProfile.objects.create(
                        user=user,
                        role='Buyer',
                        login_status=False,
                    )
        
        i=0
        for i in range(7):
                person = 'seller' + str(i)
                person_email = person + '@gmail.com'
                user = User.objects.create_user(
                            username=person_email,
                            email=person_email,
                            password="test",
                            is_active=True
                        )
                group, _ = Group.objects.get_or_create(name="Seller")
                user.groups.add(group)
                sellerUser = UserProfile.objects.create(
                            user=user,
                            role='Seller',
                            login_status=False,
                            seller_approved=True,
                            seller_request_pending=False
                        )


    #def testAccount(self):
    #    person = User.objects.get(email="admin1@gmail.com")
    #    self.assertEqual(person.email, "admin1@gmail.com")
    #def testBuyer(self):
    #    userPerson = User.objects.get(email='buyer1@gmail.com')
    #    userProfilePerson = UserProfile.objects.get(user=userPerson)
    #    self.assertEqual(userProfilePerson.role, 'Buyer')
    #def testSeller(self):
    #    self.assertEqual(UserProfile.objects.get(user=User.objects.get(email='seller1@gmail.com')).role, 'Seller')
    #def testAdmin(self):
    #    self.assertEqual(UserProfile.objects.get(user=User.objects.get(email='admin1@gmail.com')).role, 'Admin')
    def testIsBuyer(self):
        self.assertEqual(is_buyer(User.objects.get(email="buyer0@gmail.com")), True)
    def testIsSeller(self):
        self.assertEqual(is_seller(User.objects.get(email="seller0@gmail.com")), True)
    def testIsAdmin(self):
        self.assertEqual(is_admin(User.objects.get(email="admin0@gmail.com")), True)

    def testIsNotBuyer(self):
        self.assertEqual(is_buyer(User.objects.get(email="admin0@gmail.com")), True)
    def testIsNotSeller(self):
        self.assertEqual(is_seller(User.objects.get(email="buyer0@gmail.com")), True)
    def testIsNotAdmin(self):
        self.assertEqual(is_admin(User.objects.get(email="seller0@gmail.com")), True)

#class testLoginBearer(TestCase):
#    def setup(self):
#        request = ()
#    def testAuthenticatedUser(self):
#        self.assertEqual(login_bearer(), redirect('admin_home'))



#unit - request pages
#unit - manage profile
#unit - logout

#adminpanel
#config
#core
#interactions
#listings
#primary_pages