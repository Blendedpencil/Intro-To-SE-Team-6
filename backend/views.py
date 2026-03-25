from django.contrib.auth import authenticate, login, logout as auth_logout
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.shortcuts import render, redirect
from rest_framework.authtoken.models import Token


def has_group(user, group_name: str) -> bool:
    return user.is_authenticated and user.groups.filter(name=group_name).exists()


def is_buyer(user) -> bool:
    return has_group(user, "Buyer")


def is_seller(user) -> bool:
    return has_group(user, "Seller")


def is_admin(user) -> bool:
    return has_group(user, "Admin")


def get_user_from_session_token(request):
    token_key = request.session.get("bearer_token")
    if not token_key:
        return None

    try:
        token = Token.objects.select_related("user").get(key=token_key)
        return token.user
    except Token.DoesNotExist:
        return None


def login_bearer(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        user = authenticate(request, username=email, password=password)

        if user:
            login(request, user)
            token, _ = Token.objects.get_or_create(user=user)

            request.session["bearer_token"] = token.key
            request.session["bearer_email"] = email

            if is_admin(user):
                return redirect("adminHome")
            if is_seller(user):
                return redirect("seller_page")
            if is_buyer(user):
                return redirect("buyer_page")

            messages.error(request, "No role assigned.")
            return redirect("loginPage")

        messages.error(request, "Invalid credentials.")
        return redirect("loginPage")

    return render(request, "accounts/loginPage.html")


def register_page(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("loginPage")

        if User.objects.filter(username=email).exists():
            messages.error(request, "An account with that email already exists.")
            return redirect("loginPage")

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )

        buyer_group, _ = Group.objects.get_or_create(name="Buyer")
        user.groups.add(buyer_group)

        messages.success(request, "Buyer account created successfully. Please log in.")
        return redirect("loginPage")

    return redirect("loginPage")


def admin_create_account(request):
    if request.method == "POST":
        admin_name = request.POST["adminName"]
        admin_email = request.POST["adminEmail"]
        admin_pass = request.POST["adminPass"]
        confirm_admin_pass = request.POST["confirmAdminPass"]

        if admin_pass != confirm_admin_pass:
            messages.error(request, "Passwords do not match.")
            return redirect("adminCreateAccount")

        if User.objects.filter(username=admin_email).exists():
            messages.error(request, "An admin account with that email already exists.")
            return redirect("adminCreateAccount")

        user = User.objects.create_user(
            username=admin_email,
            email=admin_email,
            password=admin_pass,
            first_name=admin_name
        )

        admin_group, _ = Group.objects.get_or_create(name="Admin")
        user.groups.add(admin_group)

        messages.success(request, "Admin account created successfully. Please log in.")
        return redirect("loginPage")

    return render(request, "accounts/adminCreateAccount.html")


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


def logout_bearer(request):
    auth_logout(request)

    token_key = request.session.get("bearer_token")

    request.session.pop("bearer_token", None)
    request.session.pop("bearer_email", None)

    if token_key:
        Token.objects.filter(key=token_key).delete()

    return redirect("loginPage")

#database functions
from backend.models import Saved_Listings, Listings, Reports, Admins, Sellers, Buyers, Users

#USER
#verifyLogin

#logout
#reportUser
#updateProfile
#changeUsername
#changePassword

#BUYER
#addToSavedListings
#removeFromSavedListings
#registerBuyerAccount

#BUYER VIEW APPLICATIONS
#addApplicationToBuyerList
#removeApplicationFromBuyerList

#SELLER
#addListing

#deleteListing

#editListing
#sellerAcceptOffer
#sellerRejectOffer


#SELLER VIEW APPLICATIONS
#addApplicationToSellerList
def addApplicationToSellerList():
    Saved_Listings.objects.create(id=1, buyer=1, listing=1)
#removeApplicationFromSellerList
def removeApplicationFromSellerList():
    Saved_Listings.objects.delete(id=1)

