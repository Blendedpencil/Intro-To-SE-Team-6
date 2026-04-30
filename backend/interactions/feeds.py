from django.contrib.syndication.views import Feed
from django.urls import reverse
from .models import BuyerApplication, SellerFeedToken


class SellerApplicationsFeed(Feed):
    """
    Individual RSS feed per seller.
    Each seller gets a unique URL using their UUID token.
    Their warehousing software subscribes to this URL to automatically
    receive new buyer applications.

    Feed URL: /feeds/seller/<uuid:token>/

    Each item in the feed includes:
      - Product name      (listing title)
      - Ship-to address   (listing address)
      - Date/time         (when application was submitted)
    """

    def get_object(self, request, token):
        # token from URL identifies exactly which seller
        # returns 404 automatically if token not found or inactive
        return SellerFeedToken.objects.get(token=token, is_active=True)

    def title(self, feed_token):
        return f"Applications — {feed_token.seller.get_full_name() or feed_token.seller.username}"

    def description(self, feed_token):
        return f"Incoming buyer applications for {feed_token.seller.username}"

    def link(self, feed_token):
        return f"/seller/dashboard/"

    def items(self, feed_token):
        # ONLY returns this seller's applications
        return BuyerApplication.objects.filter(
            seller=feed_token.seller
        ).exclude(
            status='Deleted'
        ).order_by('-created_at')[:50]

    def item_title(self, item):
        # Product name = listing title (TA requirement #1)
        return f"New Application: {item.listing.title}"

    def item_description(self, item):
        # All 3  requirements included here
        return (
            f"Product: {item.listing.title} | "                                         # TA requirement #1
            f"Ship To: {item.listing.address} | "                                       # TA requirement #2
            f"Order Placed: {item.created_at.strftime('%Y-%m-%d %H:%M:%S')} | "        # TA requirement #3
            f"Buyer: {item.first_name} {item.last_name} | "
            f"Offer Amount: ${item.offer_amount} | "
            f"Status: {item.status}"
        )

    def item_pubdate(self, item):
        # Date and time of the order (TA requirement #3)
        return item.created_at

    def item_link(self, item):
        return reverse('application-detail', args=[item.pk])