from django.shortcuts import render, redirect


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
    return render(request, 'listings/create_listing.html')