from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
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
    if request.user.is_authenticated:
        if is_admin(request.user):
            return redirect('admin_home')
        elif is_seller(request.user):
            return redirect('seller_dashboard')
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

        profile, _ = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'role': 'Buyer',
                'login_status': False,
                'seller_approved': False,
                'seller_request_pending': False,
            }
        )

        if profile.role == 'Seller' and not profile.seller_approved:
            return render(request, 'accounts/auth.html', {
                'error': 'Seller accounts must be approved by an admin before login.'
            })

        login(request, user)

        token, _ = Token.objects.get_or_create(user=user)
        request.session['bearer_token'] = token.key
        request.session['bearer_email'] = email

        profile.login_status = True
        profile.save()

        if is_admin(user):
            return redirect('admin_home')
        elif is_seller(user):
            return redirect('seller_dashboard')
        else:
            return redirect('buyer_page')

    return render(request, 'accounts/auth.html')


def register_page(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

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
            login_status=False,
            seller_approved=False,
            seller_request_pending=False
        )

        return render(request, 'accounts/auth.html', {
            'success': 'Buyer account created successfully. Please log in.'
        })

    return render(request, 'accounts/auth.html')


def seller_register_page(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        if not email or not password:
            return render(request, 'accounts/seller_register.html', {
                'error': 'Email and password are required.'
            })

        if User.objects.filter(username=email).exists():
            return render(request, 'accounts/seller_register.html', {
                'error': 'An account with that email already exists.'
            })

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            is_active=False
        )

        seller_group, _ = Group.objects.get_or_create(name='Seller')
        user.groups.add(seller_group)

        UserProfile.objects.create(
            user=user,
            role='Seller',
            login_status=False,
            seller_approved=False,
            seller_request_pending=True
        )

        return render(request, 'accounts/seller_register.html', {
            'success': 'Seller request submitted. Wait for admin approval before logging in.'
        })

    return render(request, 'accounts/seller_register.html')


def seller_login_page(request):
    if request.user.is_authenticated:
        if is_admin(request.user):
            return redirect('admin_home')
        elif is_seller(request.user):
            return redirect('seller_dashboard')
        else:
            return redirect('buyer_page')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        user = authenticate(request, username=email, password=password)

        if user is None:
            return render(request, 'accounts/seller_login.html', {
                'error': 'Invalid email or password.'
            })

        profile = UserProfile.objects.filter(user=user).first()

        if not profile or profile.role != 'Seller':
            return render(request, 'accounts/seller_login.html', {
                'error': 'This is not a seller account.'
            })

        if not user.is_active:
            if profile.seller_request_pending and not profile.seller_approved:
                return render(request, 'accounts/seller_login.html', {
                    'error': 'Your seller account is still waiting for admin approval.'
                })

            return render(request, 'accounts/seller_login.html', {
                'error': 'This account has been banned or disabled.'
            })

        if not profile.seller_approved:
            return render(request, 'accounts/seller_login.html', {
                'error': 'Your seller account has not been approved yet.'
            })

        login(request, user)

        token, _ = Token.objects.get_or_create(user=user)
        request.session['bearer_token'] = token.key
        request.session['bearer_email'] = email

        profile.login_status = True
        profile.save()

        return redirect('seller_dashboard')

    return render(request, 'accounts/seller_login.html')


def admin_create_account(request):
    if not request.user.is_authenticated or not is_admin(request.user):
        return redirect('loginPage')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        role = request.POST.get('role', '').strip()

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

        is_active = True
        seller_approved = False
        seller_request_pending = False

        if role == 'Seller':
            is_active = False
            seller_request_pending = True

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            is_active=is_active
        )

        group, _ = Group.objects.get_or_create(name=role)
        user.groups.add(group)

        UserProfile.objects.create(
            user=user,
            role=role,
            login_status=False,
            seller_approved=seller_approved,
            seller_request_pending=seller_request_pending
        )

        if role == 'Seller':
            message = 'Seller account request created. Admin approval is still required.'
        else:
            message = f'{role} account created successfully.'

        return render(request, 'accounts/admin_create_account.html', {
            'success': message
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
        return redirect('seller_login_page')

    if not is_seller(request.user):
        return redirect('seller_login_page')

    profile = UserProfile.objects.filter(user=request.user).first()
    if not profile or not profile.seller_approved:
        return redirect('seller_login_page')

    return render(request, 'listings/seller_dashboard.html')


def admin_page(request):
    if 'bearer_token' not in request.session or not request.user.is_authenticated:
        return redirect('admin_login_page')

    if not is_admin(request.user):
        return redirect('admin_login_page')

    return redirect('admin_home')


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


def seller_manage_profile(request):
    if 'bearer_token' not in request.session or not request.user.is_authenticated:
        return redirect('seller_login_page')

    if not is_seller(request.user):
        return redirect('seller_login_page')

    profile = UserProfile.objects.filter(user=request.user).first()

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        bio = request.POST.get('bio', '').strip()

        if not name or not email or not phone:
            return render(request, 'accounts/seller_manage_profile.html', {
                'error': 'Fill in required fields.',
                'profile': profile
            })

        existing_user = User.objects.filter(username=email).exclude(id=request.user.id).first()
        if existing_user:
            return render(request, 'accounts/seller_manage_profile.html', {
                'error': 'That email is already being used.',
                'profile': profile
            })

        parts = name.split(maxsplit=1)
        request.user.first_name = parts[0] if parts else ''
        request.user.last_name = parts[1] if len(parts) > 1 else ''
        request.user.email = email
        request.user.username = email
        request.user.save()

        if profile:
            profile.phone = phone
            profile.bio = bio
            profile.save()

        request.session['bearer_email'] = email

        return render(request, 'accounts/seller_manage_profile.html', {
            'success': 'Profile saved.',
            'profile': profile
        })

    return render(request, 'accounts/seller_manage_profile.html', {
        'profile': profile
    })


def logout_bearer(request):
    if request.user.is_authenticated:
        profile, _ = UserProfile.objects.get_or_create(
            user=request.user,
            defaults={
                'role': 'Buyer',
                'seller_approved': False,
                'seller_request_pending': False
            }
        )
        profile.login_status = False
        profile.save()

    logout(request)
    request.session.flush()
    return redirect('homepage')