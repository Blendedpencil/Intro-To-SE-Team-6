from django.contrib.auth.models import User, Group
from django.core.files.uploadedfile import SimpleUploadedFile

from accounts.models import UserProfile
from listings.models import Listing, SavedListing
from interactions.models import BuyerApplication, Notification, Complaint


PASSWORD = "testpass123"


def create_user_with_role(username, role, password=PASSWORD, is_active=True):
    user = User.objects.create_user(
        username=username,
        email=username,
        password=password,
        is_active=is_active
    )

    group, _ = Group.objects.get_or_create(name=role)
    user.groups.add(group)

    UserProfile.objects.update_or_create(
        user=user,
        defaults={
            "role": role,
            "login_status": False,
            "seller_approved": role == "Seller",
            "seller_request_pending": False,
        }
    )

    return user


def create_buyer(username="buyer@test.com"):
    return create_user_with_role(username, "Buyer")


def create_seller(username="seller@test.com"):
    return create_user_with_role(username, "Seller")


def create_admin(username="admin@test.com"):
    return create_user_with_role(username, "Admin")


def create_pending_seller(username="pending-seller@test.com"):
    user = User.objects.create_user(
        username=username,
        email=username,
        password=PASSWORD,
        is_active=False
    )

    group, _ = Group.objects.get_or_create(name="Seller")
    user.groups.add(group)

    UserProfile.objects.update_or_create(
        user=user,
        defaults={
            "role": "Seller",
            "login_status": False,
            "seller_approved": False,
            "seller_request_pending": True,
        }
    )

    return user


def login_with_session(client, user, password=PASSWORD):
    client.login(username=user.username, password=password)

    session = client.session
    session["bearer_token"] = "test-token"
    session["bearer_email"] = user.username
    session.save()


def fake_png(name="test.png"):
    return SimpleUploadedFile(
        name,
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01",
        content_type="image/png"
    )


def fake_jpg(name="test.jpg"):
    return SimpleUploadedFile(
        name,
        b"\xff\xd8\xff\xe0" + b"0" * 20,
        content_type="image/jpeg"
    )


def fake_pdf(name="test.pdf"):
    return SimpleUploadedFile(
        name,
        b"%PDF-1.4 test pdf",
        content_type="application/pdf"
    )


def fake_txt(name="bad.txt"):
    return SimpleUploadedFile(
        name,
        b"bad file",
        content_type="text/plain"
    )


def create_listing(
    seller=None,
    title="Modern Test House",
    price=250000,
    location="Starkville, MS",
    style="Modern",
    description="A test listing.",
    bedrooms=3,
    bathrooms=2,
    square_footage=1800,
    is_active=True,
    is_sold=False,
    is_approved=True,
    approval_pending=False,
):
    if seller is None:
        seller = create_seller()

    return Listing.objects.create(
        seller=seller,
        title=title,
        price=price,
        location=location,
        style=style,
        description=description,
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        square_footage=square_footage,
        is_active=is_active,
        is_sold=is_sold,
        is_approved=is_approved,
        approval_pending=approval_pending
    )


def create_approved_listing(seller=None, title="Modern Test House"):
    return create_listing(
        seller=seller,
        title=title,
        is_active=True,
        is_sold=False,
        is_approved=True,
        approval_pending=False
    )


def create_pending_listing(seller=None, title="Pending Test House"):
    return create_listing(
        seller=seller,
        title=title,
        is_active=True,
        is_sold=False,
        is_approved=False,
        approval_pending=True
    )


def create_deleted_listing(seller=None, title="Deleted Test House"):
    return create_listing(
        seller=seller,
        title=title,
        is_active=False,
        is_sold=False,
        is_approved=True,
        approval_pending=False
    )


def create_sold_listing(seller=None, title="Sold Test House"):
    return create_listing(
        seller=seller,
        title=title,
        is_active=False,
        is_sold=True,
        is_approved=True,
        approval_pending=False
    )


def create_saved_listing(buyer=None, listing=None):
    if buyer is None:
        buyer = create_buyer()

    if listing is None:
        listing = create_approved_listing()

    return SavedListing.objects.create(
        buyer=buyer,
        listing=listing
    )


def create_application(
    buyer=None,
    seller=None,
    listing=None,
    status="Pending"
):
    if seller is None:
        seller = create_seller()

    if buyer is None:
        buyer = create_buyer()

    if listing is None:
        listing = create_approved_listing(seller=seller)

    return BuyerApplication.objects.create(
        buyer=buyer,
        seller=seller,
        listing=listing,
        first_name="Test",
        last_name="Buyer",
        email=buyer.username,
        status=status
    )


def create_notification(recipient, sender=None, application=None):
    if sender is None:
        sender = create_admin()

    return Notification.objects.create(
        recipient=recipient,
        sender=sender,
        title="Test Notification",
        message="This is a test notification.",
        application=application
    )


def create_complaint(reporter=None, listing=None):
    if reporter is None:
        reporter = create_buyer()

    if listing is None:
        listing = create_approved_listing()

    return Complaint.objects.create(
        reporter=reporter,
        reported_user=listing.seller,
        listing=listing,
        subject="Misleading Listing",
        message="This listing has an issue."
    )