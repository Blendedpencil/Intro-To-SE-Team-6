from django.shortcuts import render
from listings.models import Listing, SavedListing
from listings.models import Listing
from django.db.models import Q

def homepage(request):
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

    return render(request, 'core/homepage.html', {
        'listings': listings,
        'location': location,
        'style': style,
        'min_price': min_price,
        'max_price': max_price,
        'sort': sort,
    })


def contact_page(request):
    return render(request, 'core/contact_page.html')


def error_access_denied(request):
    return render(request, 'core/error_access_denied.html')