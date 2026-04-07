from django.contrib.auth.models import User, Group
from accounts.models import UserProfile
from listings.models import Listing
from django.core.files.uploadedfile import SimpleUploadedFile


def create_user_with_role(index: int, role: str, password: str = "test", is_active: bool = True):
    """
    Creates a user with a role: Admin, Buyer, Seller
    """
    username = f"{role.lower()}{index}@gmail.com"

    user = User.objects.create_user(
        username=username,
        email=username,
        password=password,
        is_active=is_active
    )

    # Assign group
    group, _ = Group.objects.get_or_create(name=role)
    user.groups.add(group)

    # Create profile
    profile_data = {
        "user": user,
        "role": role,
        "login_status": False,
    }

    if role == "Seller":
        profile_data.update({
            "seller_approved": True,
            "seller_request_pending": False
        })

    if role == "Admin":
        profile_data.update({
            "seller_approved": False,
            "seller_request_pending": False
        })

    UserProfile.objects.create(**profile_data)

    return user


def create_admin(index=0):
    return create_user_with_role(index, "Admin")


def create_buyer(index=0):
    return create_user_with_role(index, "Buyer")


def create_seller(index=0, approved=True):
    user = create_user_with_role(index, "Seller")

    profile = user.userprofile
    profile.seller_approved = approved
    profile.seller_request_pending = not approved
    profile.save()

    return user


def seed_basic_users():
    """
    Creates:
    - 5 admins
    - 5 buyers
    - 7 sellers
    """
    admins = [create_admin(i) for i in range(5)]
    buyers = [create_buyer(i) for i in range(5)]
    sellers = [create_seller(i) for i in range(7)]

    return admins, buyers, sellers


def create_listing_for_seller(
    seller,
    title="House",
    price=100000,
    location="Test Lane",
    style="Other",
    description="Accurate Description",
    bedrooms=0,
    bathrooms=0,
    square_footage=0,
    is_active=True,
    is_sold=False,
    is_approved=True,
    approval_pending=False,
    image=None
):
    """
    Creates a listing tied to a seller
    """

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
        approval_pending=approval_pending,
        image=image
    )


def create_pending_listing(seller, index=0):
    """
    Listing waiting for admin approval
    """
    return create_listing_for_seller(
        seller=seller,
        title=f"Pending House {index}",
        price=200000 + index,
        location=f"{index} Pending Lane",
        is_approved=False,
        approval_pending=True
    )


def create_approved_listing(seller, index=0):
    """
    Visible listing
    """
    return create_listing_for_seller(
        seller=seller,
        title=f"Approved House {index}",
        price=300000 + index,
        location=f"{index} Approved Lane",
        is_approved=True,
        approval_pending=False
    )


def seed_listings():
    """
    Creates listings for all sellers
    """
    listings = []

    for i in range(7):
        seller = User.objects.get(username=f"seller{i}@gmail.com")

        listing = create_listing_for_seller(
            seller=seller,
            title=f"House {i}",
            price=100000 + i,
            location=f"{i} Lane",
            style="Other",
            description="Seeded Listing"
        )

        listings.append(listing)

    return listings





def fake_image():
    return SimpleUploadedFile(
        "house.png",
        b"\x89PNG\r\n\x1a\nfakepngdata",
        content_type="image/png"
    )


def fake_pdf(name="file.pdf"):
    return SimpleUploadedFile(
        name,
        b"%PDF-1.4 fake pdf content",
        content_type="application/pdf"
    )


def fake_jpg():
    return SimpleUploadedFile(
        "image.jpg",
        b"\xff\xd8\xff fakejpgdata",
        content_type="image/jpeg"
    )