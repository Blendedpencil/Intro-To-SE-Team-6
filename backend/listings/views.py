from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.views.decorators.cache import never_cache
from django.http import HttpResponse
from django.urls import reverse
from django.utils.feedgenerator import Rss201rev2Feed
from .models import Listing, SavedListing
from interactions.models import BuyerApplication, Notification
from interactions.utils import (
    is_valid_uploaded_file,
    ALLOWED_LISTING_IMAGE_MIME_TYPES,
    ALLOWED_LISTING_IMAGE_EXTENSIONS,
)


def is_buyer(user):
    return user.groups.filter(name='Buyer').exists()


def is_seller(user):
    return user.groups.filter(name='Seller').exists()


@never_cache
def buyer_page(request):
    search = request.GET.get('search', '').strip()

    listings = Listing.objects.select_related(
        'seller',
        'seller__userprofile'
    ).filter(
        is_active=True,
        is_sold=False,
        is_approved=True,
        approval_pending=False
    ).order_by('-created_at')

    if search:
        listings = listings.filter(
            Q(title__icontains=search) |
            Q(style__icontains=search) |
            Q(location__icontains=search)
        )

    return render(request, 'listings/buyer_page.html', {
        'listings': listings,
        'search': search
    })


@never_cache
def listing_details(request, listing_id):
    listing = get_object_or_404(
        Listing.objects.select_related('seller', 'seller__userprofile'),
        id=listing_id,
        is_active=True,
        is_sold=False,
        is_approved=True,
        approval_pending=False
    )

    saved_listings = []
    already_saved = False
    can_compare = False

    if request.user.is_authenticated and is_buyer(request.user):
        saved_listings = SavedListing.objects.filter(
            buyer=request.user
        ).select_related('listing')
        already_saved = saved_listings.filter(listing=listing).exists()
        can_compare = saved_listings.exclude(listing=listing).exists()

    return render(request, 'listings/listing_details.html', {
        'listing': listing,
        'saved_listings': saved_listings,
        'already_saved': already_saved,
        'can_compare': can_compare
    })


def save_listing(request, listing_id):
    if not request.user.is_authenticated or not is_buyer(request.user):
        return redirect('error_access_denied')

    listing = get_object_or_404(
        Listing,
        id=listing_id,
        is_active=True,
        is_sold=False,
        is_approved=True,
        approval_pending=False
    )

    SavedListing.objects.get_or_create(
        buyer=request.user,
        listing=listing
    )

    return redirect('listing_details', listing_id=listing.id)


@never_cache
def wishlist_page(request):
    if not request.user.is_authenticated or not is_buyer(request.user):
        return redirect('error_access_denied')

    saved_items = SavedListing.objects.filter(
        buyer=request.user,
        listing__is_sold=False
    ).select_related('listing', 'listing__seller').order_by('-saved_at')

    return render(request, 'listings/wishlist_page.html', {
        'saved_items': saved_items
    })


def remove_saved_listing(request, listing_id):
    if not request.user.is_authenticated or not is_buyer(request.user):
        return redirect('error_access_denied')

    SavedListing.objects.filter(
        buyer=request.user,
        listing_id=listing_id
    ).delete()

    return redirect('wishlist_page')


@never_cache
def comparison_page(request):
    if not request.user.is_authenticated or not is_buyer(request.user):
        return redirect('error_access_denied')

    first_id = request.GET.get('first')
    second_id = request.GET.get('second')

    first_listing = get_object_or_404(
        Listing,
        id=first_id,
        is_active=True,
        is_sold=False,
        is_approved=True,
        approval_pending=False
    ) if first_id else None

    second_listing = get_object_or_404(
        Listing,
        id=second_id,
        is_active=True,
        is_sold=False,
        is_approved=True,
        approval_pending=False
    ) if second_id else None

    return render(request, 'listings/comparison_page.html', {
        'first_listing': first_listing,
        'second_listing': second_listing
    })


@never_cache
def create_listing(request):
    if 'bearer_token' not in request.session or not request.user.is_authenticated:
        return redirect('seller_login_page')

    if not is_seller(request.user):
        return redirect('seller_login_page')

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        price = request.POST.get('price', '').strip()
        location = request.POST.get('location', '').strip()
        style = request.POST.get('style', '').strip()
        description = request.POST.get('description', '').strip()
        bedrooms = request.POST.get('bedrooms', '0').strip()
        bathrooms = request.POST.get('bathrooms', '0').strip()
        square_footage = request.POST.get('square_footage', '0').strip()
        image = request.FILES.get('image')

        if not title or not price or not location or not description:
            return render(request, 'listings/seller_create_listing.html', {
                'error': 'Please fill in all required fields.'
            })

        try:
            bedrooms = int(bedrooms) if bedrooms else 0
            bathrooms = int(bathrooms) if bathrooms else 0
            square_footage = int(square_footage) if square_footage else 0
        except ValueError:
            return render(request, 'listings/seller_create_listing.html', {
                'error': 'Bedrooms, bathrooms, and square footage must be whole numbers.'
            })

        if bedrooms < 0 or bathrooms < 0 or square_footage < 0:
            return render(request, 'listings/seller_create_listing.html', {
                'error': 'Bedrooms, bathrooms, and square footage cannot be negative.'
            })

        if image and not is_valid_uploaded_file(
            image,
            ALLOWED_LISTING_IMAGE_MIME_TYPES,
            ALLOWED_LISTING_IMAGE_EXTENSIONS
        ):
            return render(request, 'listings/seller_create_listing.html', {
                'error': 'Listing images must be PNG, JPG, or JPEG files only.'
            })

        Listing.objects.create(
            seller=request.user,
            title=title,
            price=price,
            location=location,
            style=style if style else 'Other',
            description=description,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            square_footage=square_footage,
            image=image,
            is_active=True,
            is_sold=False,
            is_approved=False,
            approval_pending=True
        )

        return render(request, 'listings/seller_create_listing.html', {
            'success': 'Listing submitted successfully. It must be approved by an admin before it becomes visible.'
        })

    return render(request, 'listings/seller_create_listing.html')


@never_cache
def seller_dashboard(request):
    if not request.user.is_authenticated or not is_seller(request.user):
        return redirect('seller_login_page')

    listings = Listing.objects.filter(seller=request.user).order_by('-created_at')
    applications = BuyerApplication.objects.filter(
        seller=request.user
    ).select_related('listing', 'buyer').order_by('-created_at')

    return render(request, 'listings/seller_dashboard.html', {
        'listings': listings,
        'applications': applications
    })


@never_cache
def seller_edit_listing(request):
    if 'bearer_token' not in request.session or not request.user.is_authenticated:
        return redirect('seller_login_page')

    if not is_seller(request.user):
        return redirect('seller_login_page')

    seller_listings = Listing.objects.filter(
        seller=request.user
    ).order_by('-created_at')

    listing_id = request.GET.get('listing_id') or request.POST.get('listing_id')
    selected_listing = None

    if listing_id:
        selected_listing = get_object_or_404(
            Listing,
            id=listing_id,
            seller=request.user
        )

    if request.method == 'POST':
        if not selected_listing:
            return render(request, 'listings/seller_edit_listing.html', {
                'listings': seller_listings,
                'error': 'Please choose a listing to edit.'
            })

        if not selected_listing.is_active or selected_listing.is_sold:
            return render(request, 'listings/seller_edit_listing.html', {
                'listings': seller_listings,
                'selected_listing': selected_listing,
                'error': 'This listing can no longer be edited.'
            })

        title = request.POST.get('title', '').strip()
        price = request.POST.get('price', '').strip()
        location = request.POST.get('location', '').strip()
        style = request.POST.get('style', '').strip()
        bedrooms = request.POST.get('bedrooms', '0').strip()
        bathrooms = request.POST.get('bathrooms', '0').strip()
        square_footage = request.POST.get('square_footage', '0').strip()
        description = request.POST.get('description', '').strip()
        image = request.FILES.get('image')

        if not title or not price or not location or not description:
            return render(request, 'listings/seller_edit_listing.html', {
                'listings': seller_listings,
                'selected_listing': selected_listing,
                'error': 'Please fill in all required fields.'
            })

        try:
            bedrooms = int(bedrooms) if bedrooms else 0
            bathrooms = int(bathrooms) if bathrooms else 0
            square_footage = int(square_footage) if square_footage else 0
        except ValueError:
            return render(request, 'listings/seller_edit_listing.html', {
                'listings': seller_listings,
                'selected_listing': selected_listing,
                'error': 'Bedrooms, bathrooms, and square footage must be whole numbers.'
            })

        if bedrooms < 0 or bathrooms < 0 or square_footage < 0:
            return render(request, 'listings/seller_edit_listing.html', {
                'listings': seller_listings,
                'selected_listing': selected_listing,
                'error': 'Bedrooms, bathrooms, and square footage cannot be negative.'
            })

        selected_listing.title = title
        selected_listing.price = price
        selected_listing.location = location
        selected_listing.style = style
        selected_listing.bedrooms = bedrooms
        selected_listing.bathrooms = bathrooms
        selected_listing.square_footage = square_footage
        selected_listing.description = description

        if image:
            selected_listing.image = image

        selected_listing.save()

        return redirect('seller_dashboard')

    return render(request, 'listings/seller_edit_listing.html', {
        'listings': seller_listings,
        'selected_listing': selected_listing
    })


@never_cache
def seller_negotiation(request):
    if not request.user.is_authenticated or not is_seller(request.user):
        return redirect('seller_login_page')

    application_id = request.GET.get('application_id')

    application = get_object_or_404(
        BuyerApplication.objects.select_related('listing', 'buyer', 'seller'),
        id=application_id,
        seller=request.user
    )

    locked_statuses = [
        'AcceptedBySeller',
        'RejectedBySeller',
        'RejectedByBuyer',
        'AcceptedByBuyer',
        'Deleted',
        'Paid',
    ]

    if request.method == 'POST':
        if application.status in locked_statuses:
            return render(request, 'listings/seller_negotiation.html', {
                'application': application,
                'error': 'This decision has already been finalized and cannot be changed.'
            })

        action = request.POST.get('action')

        if action == 'accept':
            application.status = 'AcceptedBySeller'
            application.save()

            Notification.objects.create(
                recipient=application.buyer,
                sender=request.user,
                title='Application Accepted',
                message=f'Your application for "{application.listing.title}" was accepted by the seller.',
                application=application
            )

        elif action == 'reject':
            application.status = 'RejectedBySeller'
            application.save()

            Notification.objects.create(
                recipient=application.buyer,
                sender=request.user,
                title='Application Rejected',
                message=f'Your application for "{application.listing.title}" was rejected by the seller.',
                application=application
            )

        elif action == 'counter':
            counter_amount = request.POST.get('counter_amount')
            if counter_amount:
                application.counter_amount = counter_amount
                application.status = 'CounterSent'
                application.save()

                Notification.objects.create(
                    recipient=application.buyer,
                    sender=request.user,
                    title='Counter Offer Sent',
                    message=f'The seller sent a counter offer for "{application.listing.title}".',
                    application=application
                )

        return redirect(f'/listings/seller/negotiation/?application_id={application.id}')

    return render(request, 'listings/seller_negotiation.html', {
        'application': application
    })

def latest_listings_rss(request):
    listings = Listing.objects.select_related('seller').filter(
        is_active=True,
        is_sold=False,
        is_approved=True,
        approval_pending=False
    ).order_by('-created_at')[:25]

    feed_url = request.build_absolute_uri(reverse('latest_listings_rss'))

    feed = Rss201rev2Feed(
        title='HomeZapp Latest Listings',
        link=feed_url,
        description='Latest approved public home listings on HomeZapp.'
    )

    for listing in listings:
        listing_url = request.build_absolute_uri(
            reverse('listing_details', kwargs={'listing_id': listing.id})
        )

        feed.add_item(
            title=listing.title,
            link=listing_url,
            description=(
                f"Price: ${listing.price}\n"
                f"Location: {listing.location}\n"
                f"Style: {listing.style}\n"
                f"Posted by: {listing.seller.username}\n\n"
                f"{listing.description}"
            ),
            pubdate=listing.created_at,
            unique_id=f"homezapp-listing-{listing.id}"
        )

    response = HttpResponse(content_type='application/rss+xml')
    feed.write(response, 'utf-8')
    return response

def latest_listings_page(request):
    listings = Listing.objects.select_related('seller').filter(
        is_active=True,
        is_sold=False,
        is_approved=True,
        approval_pending=False
    ).order_by('-created_at')[:25]

    return render(request, 'listings/latest_listings_page.html', {
        'listings': listings
    })