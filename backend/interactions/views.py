from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from listings.models import Listing
from .models import Complaint, Notification
# Create your views here.

def notifications_page(request):
    if 'bearer_token' not in request.session:
        return redirect('loginPage')

    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')

    return render(request, 'interactions/notifications.html', {
        'notifications': notifications
    })


def mark_notification_read(request, notification_id):
    if 'bearer_token' not in request.session:
        return redirect('loginPage')

    notification = get_object_or_404(
        Notification,
        id=notification_id,
        recipient=request.user
    )
    notification.is_read = True
    notification.save()

    return redirect('notifications_page')


def complaint_form(request):
    if 'bearer_token' not in request.session:
        return redirect('loginPage')

    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        listing_id = request.POST.get('listing_id')
        reported_user_id = request.POST.get('reported_user_id')

        listing = None
        reported_user = None

        if listing_id:
            try:
                listing = Listing.objects.get(id=listing_id)
            except Listing.DoesNotExist:
                listing = None

        if reported_user_id:
            try:
                reported_user = User.objects.get(id=reported_user_id)
            except User.DoesNotExist:
                reported_user = None

        Complaint.objects.create(
            reporter=request.user,
            reported_user=reported_user,
            listing=listing,
            subject=subject,
            message=message
        )

        return render(request, 'interactions/complaint_form.html', {
            'success': 'Complaint submitted successfully.'
        })

    return render(request, 'interactions/complaint_form.html')


def notify_seller(request):
    if 'bearer_token' not in request.session:
        return redirect('loginPage')

    if request.method == 'POST':
        seller_id = request.POST.get('seller_id')
        title = request.POST.get('title')
        message = request.POST.get('message')

        seller = get_object_or_404(User, id=seller_id)

        Notification.objects.create(
            recipient=seller,
            sender=request.user,
            title=title,
            message=message
        )

        return render(request, 'interactions/notify_seller.html', {
            'success': 'Seller notified successfully.'
        })

    return render(request, 'interactions/notify_seller.html')