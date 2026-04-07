from accounts.models import UserProfile
from adminpanel.models import BanRecord, ModerationHistory
from interactions.models import Complaint, Notification
from listings.models import Listing
from django.contrib.auth.models import User, Group
from PIL import Image

#database seeding
#admin
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

i=0
for i in range(7):
    id = i
    listing = 'listing' + str(i)
    userName = 'seller' + str(id) + '@gmail.com'
    Listing.objects.create(
            seller=User.objects.get(username=userName),
            title="House " + str(id),
            price=id+100000,
            location=str(id) + " Lane",
            style='Other',
            description="Accurate Description",
            bedrooms=0,
            bathrooms=0,
            square_footage=0,
        )

#image=(Image.open("static/images/house-stock-photo.jpg"))

#adminpanel
#-banrecords
#-moderation history

#interactions
#-complaints
#-notifications

#listings
