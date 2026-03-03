from django.contrib.auth import authenticate, login, logout as auth_logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render, redirect
from django.contrib import messages
from rest_framework.authtoken.models import Token

#This groups our users to help with permissions authorization and routing.
def has_group(user, group_name: str) -> bool:
    return user.is_authenticated and user.groups.filter(name=group_name).exists()

def is_buyer(user) -> bool:
    return has_group(user, "Buyer")

def is_seller(user) -> bool:
    return has_group(user, "Seller")

def is_admin(user) -> bool:
    return has_group(user, "Admin")


def get_user_from_session_token(request):
    """
    Looks up the token stored in session and returns the associated user.
    Returns None if token missing/invalid.
    """
    token_key = request.session.get("bearer_token")
    if not token_key:
        return None

    try:
        token = Token.objects.select_related("user").get(key=token_key)
        return token.user
    except Token.DoesNotExist:
        return None
    
#Bearer Token Login

# LOGIN 
def login_bearer(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(request, username=email, password=password)

        if user:
            login(request, user)
            token, _ = Token.objects.get_or_create(user=user)

            request.session['bearer_token'] = token.key
            request.session['bearer_email'] = email

            #Hopefully this will redirect users to the right page after logging in
            if is_admin(user):
                return redirect("adminHome")
            if is_seller(user):
                return redirect("seller_page")
            if is_buyer(user):
                return redirect("buyer_page")
            
            #Just in case a user somehow has no role
            messages.error(request, "No role assigned (Buyer/Seller/Admin).")
            return redirect("loginPage")
        
        messages.error(request, 'Invalid credentials.')

    return render(request, 'accounts/loginPage.html')


# DASHBOARD
def buyer_page(request):
    user = get_user_from_session_token(request)
    if not user:
        messages.error(request, "Please log in.")
        return redirect("loginPage")

    if not is_buyer(user):
        messages.error(request, "Unauthorized: Buyer access only.")
        return redirect("loginPage")

    return render(request, "accounts/buyer_page.html", {
        "email": user.username,
        "token": request.session.get("bearer_token"),
    })


def seller_page(request):
    user = get_user_from_session_token(request)
    if not user:
        messages.error(request, "Please log in.")
        return redirect("loginPage")

    if not is_seller(user):
        messages.error(request, "Unauthorized: Seller access only.")
        return redirect("loginPage")

    return render(request, "accounts/seller_page.html", {
        "email": user.username,
        "token": request.session.get("bearer_token"),
    })


def admin_page(request):
    user = get_user_from_session_token(request)
    if not user:
        messages.error(request, "Please log in.")
        return redirect("loginPage")

    if not is_admin(user):
        messages.error(request, "Unauthorized: Admin access only.")
        return redirect("loginPage")

    return render(request, "accounts/adminHome.html", {
        "email": user.username,
        "token": request.session.get("bearer_token"),
    })




# LOGOUT
def logout_bearer(request):
    auth_logout(request)

    token_key = request.session.get('bearer_token')

    request.session.pop('bearer_token', None)
    request.session.pop('bearer_email', None)

    if token_key:
        Token.objects.filter(key=token_key).delete()

    return redirect('loginPage')