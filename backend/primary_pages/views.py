from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User, Group
from rest_framework.authtoken.models import Token
from .models import UserProfile


def is_buyer(user):
    return user.groups.filter(name='Buyer').exists()


def is_seller(user):
    return user.groups.filter(name='Seller').exists()


def is_admin(user):
    return user.groups.filter(name='Admin').exists()


def login_bearer(request):
    # If already logged in, redirect based on role
    if request.user.is_authenticated:
        if is_admin(request.user):
            return redirect('admin_home')
        elif is_seller(request.user):
            return redirect('seller_page')
        else:
            return redirect('buyer_page')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        user = authenticate(request, username=email, password=password)

        if user is None:
            return render(request, 'accounts/auth.html', {
                'error': 'Invalid email or password.'
            })

        if not user.is_active:
            return render(request, 'accounts/auth.html', {
                'error': 'This account has been banned or disabled.'
            })

        login(request, user)

        token, _ = Token.objects.get_or_create(user=user)


        request.session['bearer_token'] = token.key
        request.session['bearer_email'] = email


        profile, _ = UserProfile.objects.get_or_create(
            user=user,
            defaults={'role': 'Buyer'}  
        )
        profile.login_status = True
        profile.save()

        if is_admin(user):
            return redirect('admin_home')

        elif is_seller(user):
            return redirect('seller_page')

        else:
            return redirect('buyer_page')

    return render(request, 'accounts/auth.html')

def register_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            return render(request, 'accounts/auth.html', {
                'error': 'Email and password are required.'
            })

        if User.objects.filter(username=email).exists():
            return render(request, 'accounts/auth.html', {
                'error': 'An account with that email already exists.'
            })

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )

        buyer_group, _ = Group.objects.get_or_create(name='Buyer')
        user.groups.add(buyer_group)

        UserProfile.objects.create(
            user=user,
            role='Buyer',
            login_status=False
        )

        return render(request, 'accounts/auth.html', {
            'success': 'Account created successfully. Please log in.'
        })

    return render(request, 'accounts/auth.html')


def admin_create_account(request):
    if not request.user.is_authenticated or not is_admin(request.user):
        return redirect('loginPage')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')

        if not email or not password or not role:
            return render(request, 'accounts/admin_create_account.html', {
                'error': 'Email, password, and role are required.'
            })

        if role not in ['Buyer', 'Seller', 'Admin']:
            return render(request, 'accounts/admin_create_account.html', {
                'error': 'Invalid role selected.'
            })

        if User.objects.filter(username=email).exists():
            return render(request, 'accounts/admin_create_account.html', {
                'error': 'That email is already in use.'
            })

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )

        group, _ = Group.objects.get_or_create(name=role)
        user.groups.add(group)

        UserProfile.objects.create(
            user=user,
            role=role,
            login_status=False
        )

        return render(request, 'accounts/admin_create_account.html', {
            'success': f'{role} account created successfully.'
        })

    return render(request, 'accounts/admin_create_account.html')


def buyer_page(request):
    if 'bearer_token' not in request.session or not request.user.is_authenticated:
        return redirect('loginPage')

    if not is_buyer(request.user):
        return redirect('loginPage')

    return render(request, 'listings/buyer_page.html')


def seller_page(request):
    if 'bearer_token' not in request.session or not request.user.is_authenticated:
        return redirect('loginPage')

    if not is_seller(request.user):
        return redirect('loginPage')

    return render(request, 'accounts/seller_dashboard.html')


def admin_page(request):
    if 'bearer_token' not in request.session or not request.user.is_authenticated:
        return redirect('loginPage')

    if not is_admin(request.user):
        return redirect('loginPage')

    return render(request, 'accounts/admin_dashboard.html')


def buyer_manageprofile(request):
    if 'bearer_token' not in request.session or not request.user.is_authenticated:
        return redirect('loginPage')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()

        if not first_name or not last_name or not email:
            return render(request, 'accounts/buyer_manageprofile.html', {
                'error': 'All fields are required.'
            })

        existing_user = User.objects.filter(username=email).exclude(id=request.user.id).first()
        if existing_user:
            return render(request, 'accounts/buyer_manageprofile.html', {
                'error': 'That email is already being used.'
            })

        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = email
        request.user.username = email
        request.user.save()

        request.session['bearer_email'] = email

        return render(request, 'accounts/buyer_manageprofile.html', {
            'success': 'Profile updated successfully.'
        })

    return render(request, 'accounts/buyer_manageprofile.html')


def logout_bearer(request):
    if request.user.is_authenticated:
        '''profile, _ = UserProfile.objects.get_or_create(user=request.user, defaults={'role': 'Buyer'})'''
        '''profile.login_status = False'''
        '''profile.save()'''

    logout(request)
    request.session.flush()
    return redirect('loginPage')