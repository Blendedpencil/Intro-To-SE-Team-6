#example
from django.test import TestCase

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


#accounts
#adminpanel
#config
#core
#interactions
#listings
#primary_pages