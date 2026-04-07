#example
from django.test import TestCase

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User, Group
from rest_framework.authtoken.models import Token

from accounts.models import UserProfile
from adminpanel.models import BanRecord, ModerationHistory
from interactions.models import Complaint, Notification
from listings.models import Listing
from django.contrib.auth.models import User, Group
from PIL import Image

'''
class testCase(TestCase):
    def setUp(self):
        testVar = 5
    def testThing(self):
        self.assertEqual(5, 5)

class testCase2(TestCase):
    def setUp(self):
        testVar = 5
    def testThing(self):
        self.assertEqual(5, 5)
'''

#accounts
#unit - account creation
#unit - account checking
#class testBuyerCreated(TestCase):
#    def test_buyer_exists(self):
        #pull user from database
#        self.assertEqual(User.groups.filter(name='Buyer').exists(), True)
#unit - request pages
#unit - manage profile
#unit - logout

#adminpanel
#config
#core
#interactions
#listings
#primary_pages