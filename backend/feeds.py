# django_project/feeds.py
from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords

from accounts.models import UserProfile
from adminpanel.models import BanRecord, ModerationHistory
from interactions.models import Complaint, Notification
from listings.models import Listing
from django.contrib.auth.models import User, Group
from PIL import Image


class RssTutorialsFeeds(Feed):
    title = "RSSFeed"
    link = "/rssfeed/"
    description = "Recent free tutorials on LearnDjango.com."

    def items(self):
        return Listing.objects.order_by("-updated_at")[:100]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return truncatewords(item.content, 30)

    def item_lastupdated(self, item):
        return item.updated_at