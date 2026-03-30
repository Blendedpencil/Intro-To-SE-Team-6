from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.models import User, Group
from django.db.models import Q

from accounts.models import UserProfile
from interactions.models import Complaint
from listings.models import Listing
from .models import BanRecord, ModerationHistory


def is_admin(user):
    return user.is_authenticated and user.groups.filter(name='Admin').exists()


def admin_login_page(request):
    if request.method == 'POST':
        email = request.POST.get('adminEmail', '').strip()
        password = request.POST.get('adminPass', '').strip()

        user = authenticate(request, username=email, password=password)

        if user is None:
            return render(request, 'adminpanel/admin_login.html', {
                'error': 'Invalid email or password.'
            })

        if not user.is_active:
            return render(request, 'adminpanel/admin_login.html', {
                'error': 'This account has been banned or disabled.'
            })

        if not user.groups.filter(name='Admin').exists():
            return render(request, 'adminpanel/admin_login.html', {
                'error': 'This account is not an admin account.'
            })

        login(request, user)
        request.session['bearer_token'] = 'admin-session'
        request.session['bearer_email'] = email

        profile, _ = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'role': 'Admin',
                'login_status': False,
                'seller_approved': False,
                'seller_request_pending': False
            }
        )
        profile.login_status = True
        profile.save()

        return redirect('admin_home')

    return render(request, 'adminpanel/admin_login.html')


def admin_create_account_page(request):
    if request.method == 'POST':
        admin_name = request.POST.get('adminName', '').strip()
        admin_email = request.POST.get('adminEmail', '').strip()
        admin_pass = request.POST.get('adminPass', '').strip()

        if not admin_name or not admin_email or not admin_pass:
            return render(request, 'adminpanel/admin_create_account.html', {
                'error': 'All fields are required.'
            })

        if User.objects.filter(username=admin_email).exists():
            return render(request, 'adminpanel/admin_create_account.html', {
                'error': 'An account with that email already exists.'
            })

        parts = admin_name.split(maxsplit=1)
        first_name = parts[0] if parts else ''
        last_name = parts[1] if len(parts) > 1 else ''

        user = User.objects.create_user(
            username=admin_email,
            email=admin_email,
            password=admin_pass,
            first_name=first_name,
            last_name=last_name
        )

        admin_group, _ = Group.objects.get_or_create(name='Admin')
        user.groups.add(admin_group)

        UserProfile.objects.create(
            user=user,
            role='Admin',
            login_status=False,
            seller_approved=False,
            seller_request_pending=False
        )

        return render(request, 'adminpanel/admin_create_account.html', {
            'success': 'Admin account created successfully.'
        })

    return render(request, 'adminpanel/admin_create_account.html')


def admin_home(request):
    if 'bearer_token' not in request.session or not is_admin(request.user):
        return redirect('admin_login_page')

    complaints = Complaint.objects.order_by('-created_at')

    search = request.GET.get('listing_search', '').strip()
    listings = Listing.objects.filter(is_active=True, is_sold=False).order_by('-created_at')

    if search:
        listings = listings.filter(
            Q(title__icontains=search) |
            Q(style__icontains=search) |
            Q(location__icontains=search)
        )

    return render(request, 'adminpanel/admin_home.html', {
        'complaints': complaints,
        'listings': listings,
        'listing_search': search,
    })


def admin_ban_user(request):
    if 'bearer_token' not in request.session or not is_admin(request.user):
        return redirect('admin_login_page')

    success = None
    error = None

    if request.method == 'POST' and 'ban_user' in request.POST:
        username = request.POST.get('uName', '').strip()
        reason = request.POST.get('banReason', '').strip()

        if not username or not reason:
            error = 'Username and ban reason are required.'
        else:
            try:
                user = User.objects.get(username=username)
                user.is_active = False
                user.save()

                BanRecord.objects.create(
                    user=user,
                    banned_by=request.user,
                    reason=reason
                )

                ModerationHistory.objects.create(
                    admin_user=request.user,
                    target_user=user,
                    action='BAN_USER',
                    reason=reason
                )

                success = 'User banned successfully.'
            except User.DoesNotExist:
                error = 'User not found.'

    if request.method == 'POST' and 'unban_user' in request.POST:
        user_id = request.POST.get('user_id')

        try:
            user = User.objects.get(id=user_id)
            user.is_active = True
            user.save()

            BanRecord.objects.filter(user=user).delete()

            profile = UserProfile.objects.filter(user=user, role='Seller').first()
            if profile and profile.seller_request_pending and not profile.seller_approved:
                profile.seller_approved = True
                profile.seller_request_pending = False
                profile.save()

            ModerationHistory.objects.create(
                admin_user=request.user,
                target_user=user,
                action='UNBAN_USER',
                reason='User unbanned by admin.'
            )

            success = 'User unbanned successfully.'
        except User.DoesNotExist:
            error = 'User not found.'

    banned_users = User.objects.filter(is_active=False).order_by('username')

    return render(request, 'adminpanel/admin_ban_user.html', {
        'banned_users': banned_users,
        'success': success,
        'error': error
    })


def admin_manage_profile(request):
    if 'bearer_token' not in request.session or not is_admin(request.user):
        return redirect('admin_login_page')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'change_name':
            new_name = request.POST.get('newAdminName', '').strip()
            password = request.POST.get('adminPass1', '').strip()

            if not request.user.check_password(password):
                return render(request, 'adminpanel/admin_manage_profile.html', {
                    'error': 'Password verification failed.'
                })

            parts = new_name.split(maxsplit=1)
            request.user.first_name = parts[0] if parts else ''
            request.user.last_name = parts[1] if len(parts) > 1 else ''
            request.user.save()

            return render(request, 'adminpanel/admin_manage_profile.html', {
                'success': 'Admin name updated successfully.'
            })

        elif action == 'change_email':
            new_email = request.POST.get('adminEmail', '').strip()
            password = request.POST.get('adminPass2', '').strip()

            if not request.user.check_password(password):
                return render(request, 'adminpanel/admin_manage_profile.html', {
                    'error': 'Password verification failed.'
                })

            existing = User.objects.filter(username=new_email).exclude(id=request.user.id).first()
            if existing:
                return render(request, 'adminpanel/admin_manage_profile.html', {
                    'error': 'That email is already being used.'
                })

            request.user.email = new_email
            request.user.username = new_email
            request.user.save()
            request.session['bearer_email'] = new_email

            return render(request, 'adminpanel/admin_manage_profile.html', {
                'success': 'Email updated successfully.'
            })

        elif action == 'change_password':
            new_password = request.POST.get('adminPassNew', '').strip()
            current_password = request.POST.get('adminPass3', '').strip()

            if not request.user.check_password(current_password):
                return render(request, 'adminpanel/admin_manage_profile.html', {
                    'error': 'Current password is incorrect.'
                })

            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)

            return render(request, 'adminpanel/admin_manage_profile.html', {
                'success': 'Password updated successfully.'
            })

    return render(request, 'adminpanel/admin_manage_profile.html')


def admin_report_detail(request, complaint_id):
    if 'bearer_token' not in request.session or not is_admin(request.user):
        return redirect('admin_login_page')

    complaint = get_object_or_404(Complaint, id=complaint_id)

    return render(request, 'adminpanel/admin_report.html', {
        'complaint': complaint
    })


def admin_search_user(request):
    if 'bearer_token' not in request.session or not is_admin(request.user):
        return redirect('admin_login_page')

    query = request.GET.get('searchUsers', '').strip()
    users = []

    if query:
        users = User.objects.filter(username__icontains=query).order_by('username')

    seller_requests = UserProfile.objects.filter(
        role='Seller',
        seller_request_pending=True,
        seller_approved=False
    ).select_related('user').order_by('user__username')

    return render(request, 'adminpanel/admin_search_user.html', {
        'query': query,
        'users': users,
        'seller_requests': seller_requests
    })


def approve_seller_request(request, user_id):
    if 'bearer_token' not in request.session or not is_admin(request.user):
        return redirect('admin_login_page')

    profile = get_object_or_404(UserProfile, user_id=user_id, role='Seller')
    profile.seller_approved = True
    profile.seller_request_pending = False
    profile.user.is_active = True

    profile.user.save()
    profile.save()

    ModerationHistory.objects.create(
        admin_user=request.user,
        target_user=profile.user,
        action='UNBAN_USER',
        reason='Seller account approved by admin.'
    )

    return redirect('admin_search_user')


def reject_seller_request(request, user_id):
    if 'bearer_token' not in request.session or not is_admin(request.user):
        return redirect('admin_login_page')

    profile = get_object_or_404(UserProfile, user_id=user_id, role='Seller')

    ModerationHistory.objects.create(
        admin_user=request.user,
        target_user=profile.user,
        action='BAN_USER',
        reason='Seller account request rejected by admin.'
    )

    profile.user.delete()
    return redirect('admin_search_user')


def admin_delete_listing(request, listing_id):
    if 'bearer_token' not in request.session or not is_admin(request.user):
        return redirect('admin_login_page')

    listing = get_object_or_404(Listing, id=listing_id)

    if request.method == 'POST':
        listing.is_active = False
        listing.save()

        ModerationHistory.objects.create(
            admin_user=request.user,
            action='DELETE_LISTING',
            target_listing_title=listing.title,
            reason='Listing removed by admin.'
        )

    return redirect('admin_home')


def admin_moderation_history(request):
    if 'bearer_token' not in request.session or not is_admin(request.user):
        return redirect('admin_login_page')

    history = ModerationHistory.objects.order_by('-created_at')

    return render(request, 'adminpanel/admin_moderation_history.html', {
        'history': history
    })