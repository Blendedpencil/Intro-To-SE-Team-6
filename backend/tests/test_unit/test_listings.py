from django.test import TestCase
from tests.factories import create_seller, create_listing_for_seller


class ListingsUnitTests(TestCase):

    def setUp(self):
        self.seller = create_seller()
        self.listing = create_listing_for_seller(self.seller)

    def test_listing_creation(self):
        self.assertEqual(self.listing.title, "House")
        self.assertTrue(self.listing.is_active)

    def test_listing_default_not_sold(self):
        self.assertFalse(self.listing.is_sold)