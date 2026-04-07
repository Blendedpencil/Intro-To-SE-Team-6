def role_links(request):
    user = request.user

    is_buyer = False
    is_seller = False
    is_admin = False

    if user.is_authenticated:
        is_buyer = user.groups.filter(name='Buyer').exists()
        is_seller = user.groups.filter(name='Seller').exists()
        is_admin = user.groups.filter(name='Admin').exists()

    return {
        'nav_is_authenticated': user.is_authenticated,
        'nav_is_buyer': is_buyer,
        'nav_is_seller': is_seller,
        'nav_is_admin': is_admin,
    }