from django.shortcuts import render
from listings.models import Listing, SavedListing


def homepage(request):
    listings = Listing.objects.filter(is_active=True).order_by('-created_at')

    location = request.GET.get('location', '').strip()
    style = request.GET.get('style', '').strip()
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()

    if location:
        listings = listings.filter(location__icontains=location)

    if style:
        listings = listings.filter(style__icontains=style)

    if min_price:
        try:
            listings = listings.filter(price__gte=min_price)
        except ValueError:
            pass

    if max_price:
        try:
            listings = listings.filter(price__lte=max_price)
        except ValueError:
            pass

    saved_items = []
    is_buyer = False

    if request.user.is_authenticated:
        is_buyer = request.user.groups.filter(name='Buyer').exists()
        if is_buyer:
            saved_items = SavedListing.objects.filter(
                buyer=request.user
            ).select_related('listing')

    return render(request, 'core/homepage.html', {
        'listings': listings[:10],
        'saved_items': saved_items,
        'is_buyer': is_buyer,
        'location': location,
        'style': style,
        'min_price': min_price,
        'max_price': max_price,
    })
    
def contact_page(request):
    return render(request, 'core/contact_page.html')


def error_access_denied(request):
    return render(request, 'core/error_access_denied.html')