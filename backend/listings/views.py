from django.shortcuts import render, redirect
from .models import Listing, Order
from django.http import HttpResponse
from django.urls import reverse
from django.utils.feedgenerator import Rss201rev2Feed

# Create your views here.

def buyer_page(request):
    if 'bearer_token' not in request.session:
        return redirect('loginPage')
    return render(request, 'listings/buyer_page.html')


def buyer_subpage(request):
    if 'bearer_token' not in request.session:
        return redirect('loginPage')
    return render(request, 'listings/buyer_subpage.html')


def comparison_page(request):
    if 'bearer_token' not in request.session:
        return redirect('loginPage')
    return render(request, 'listings/comparison_page.html')


def wishlist_page(request):
    if 'bearer_token' not in request.session:
        return redirect('loginPage')
    return render(request, 'listings/wishlist_page.html')


def create_listing(request):
    if 'bearer_token' not in request.session:
        return redirect('loginPage')

    if request.method == 'POST':
        title = request.POST.get('title')
        price = request.POST.get('price')
        location = request.POST.get('location')
        style = request.POST.get('style')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        if not title or not price or not location or not style or not description:
            return render(request, 'listings/create_listing.html', {
                'error': 'Please fill in all fields.'
            })

        Listing.objects.create(
             seller=request.user if request.user.is_authenticated else None,
             title=title,
             price=price,
             location=location,
             style=style,
             description=description,
             image=image
)


        return redirect('seller_dashboard')  # make sure this exists

    return render(request, 'listings/create_listing.html')

def seller_orders_rss(request, seller_id=None):
    orders = Order.objects.select_related('seller', 'listing').order_by('-placed_at')

    if seller_id is not None:
        orders = orders.filter(seller_id=seller_id)

    feed = Rss201rev2Feed(
        title='Seller Order Feed',
        link=request.build_absolute_uri(reverse('seller_orders_rss')),
        description='Recent orders for seller warehousing software.'
    )

    for order in orders:
        feed.add_item(
            title=order.product_name,
            link=request.build_absolute_uri(reverse('seller_orders_rss')),
            description=(
                f"Product: {order.product_name}\n"
                f"Ship-to address: {order.ship_to_address}\n"
                f"Order placed: {order.placed_at.isoformat()}"
            ),
            pubdate=order.placed_at,
            unique_id=f"order-{order.id}"
        )

    response = HttpResponse(content_type='application/rss+xml')
    feed.write(response, 'utf-8')
    return response
