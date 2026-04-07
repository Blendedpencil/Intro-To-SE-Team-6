from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .models import Listing, SavedListing
from interactions.models import BuyerApplication, Notification
from django.views.decorators.cache import never_cache
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
    if not request.user.is_authenticated or not is_buyer(request.user):
        return redirect('error_access_denied')

    listings = Listing.objects.filter(
        is_active=True,
        is_sold=False,
        is_approved=True,
        approval_pending=False
    )

    # FILTERING
    location = request.GET.get('location', '').strip()
    style = request.GET.get('style', '').strip()
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()

    if location:
        listings = listings.filter(location__icontains=location)

    if style:
        listings = listings.filter(style__icontains=style)

    if min_price:
        listings = listings.filter(price__gte=min_price)

    if max_price:
        listings = listings.filter(price__lte=max_price)

    # SORTING
    sort = request.GET.get('sort')

    if sort == 'price_low':
        listings = listings.order_by('price')
    elif sort == 'price_high':
        listings = listings.order_by('-price')
    elif sort == 'newest':
        listings = listings.order_by('-created_at')
    elif sort == 'location':
        listings = listings.order_by('location')
    elif sort == 'style':
        listings = listings.order_by('style')

    return render(request, 'listings/buyer_page.html', {
        'listings': listings,
        'location': location,
        'style': style,
        'min_price': min_price,
        'max_price': max_price,
        'sort': sort,
    })

@never_cache
def listing_details(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id, is_active=True, is_sold=False, is_approved=True, approval_pending=False)

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

    listing = get_object_or_404(Listing, id=listing_id, is_active=True, is_sold=False, is_approved=True, approval_pending=False)

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
    ).select_related('listing').order_by('-saved_at')

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

    first_listing = get_object_or_404(Listing, id=first_id, is_active=True, is_sold=False, is_approved=True, approval_pending=False) if first_id else None
    second_listing = get_object_or_404(Listing, id=second_id, is_active=True, is_sold=False, is_approved=True, approval_pending=False) if second_id else None

    return render(request, 'listings/comparison_page.html', {
        'first_listing': first_listing,
        'second_listing': second_listing
    })

@never_cache
def create_listing(request):
    if not request.user.is_authenticated or not is_seller(request.user):
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
            bedrooms=bedrooms or 0,
            bathrooms=bathrooms or 0,
            square_footage=square_footage or 0,
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
    if not request.user.is_authenticated or not is_seller(request.user):
        return redirect('seller_login_page')

    listings = Listing.objects.filter(seller=request.user).order_by('-created_at')
    selected_listing = None

    listing_id = request.GET.get('listing_id')
    if listing_id:
        selected_listing = get_object_or_404(Listing, id=listing_id, seller=request.user)

    if request.method == 'POST':
        listing_id = request.POST.get('listing_id')
        selected_listing = get_object_or_404(Listing, id=listing_id, seller=request.user)

        selected_listing.title = request.POST.get('title', '').strip()
        selected_listing.price = request.POST.get('price', '').strip()
        selected_listing.location = request.POST.get('location', '').strip()
        selected_listing.style = request.POST.get('style', '').strip()
        selected_listing.description = request.POST.get('description', '').strip()
        selected_listing.bedrooms = request.POST.get('bedrooms', '0').strip() or 0
        selected_listing.bathrooms = request.POST.get('bathrooms', '0').strip() or 0
        selected_listing.square_footage = request.POST.get('square_footage', '0').strip() or 0

        new_image = request.FILES.get('image')
        if new_image:
            if not is_valid_uploaded_file(
                new_image,
                ALLOWED_LISTING_IMAGE_MIME_TYPES,
                ALLOWED_LISTING_IMAGE_EXTENSIONS
            ):
                return render(request, 'listings/seller_edit_listing.html', {
                    'listings': listings,
                    'selected_listing': selected_listing,
                    'error': 'Listing images must be PNG, JPG, or JPEG files only.'
                })
            selected_listing.image = new_image

        selected_listing.save()

        return render(request, 'listings/seller_edit_listing.html', {
            'listings': listings,
            'selected_listing': selected_listing,
            'success': 'Listing updated successfully.'
        })

    return render(request, 'listings/seller_edit_listing.html', {
        'listings': listings,
        'selected_listing': selected_listing
    })

@never_cache
def seller_negotiation(request):
    if not request.user.is_authenticated or not is_seller(request.user):
        return redirect('seller_login_page')

    application_id = request.GET.get('application_id')
    application = get_object_or_404(
        BuyerApplication.objects.select_related('listing', 'buyer'),
        id=application_id,
        seller=request.user
    )

    if request.method == 'POST':
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
                message=f'Your application for "{application.listing.title}" was rejected by the seller.'
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