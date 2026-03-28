from django.shortcuts import render, redirect
from .models import Listing

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
            title=title,
            price=price,
            location=location,
            style=style,
            description=description,
            image=image
        )

        return redirect('seller_dashboard')  # make sure this exists

    return render(request, 'listings/create_listing.html')
