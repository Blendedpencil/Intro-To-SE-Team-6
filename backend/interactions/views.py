from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import never_cache

from listings.models import Listing, SavedListing
from .models import BuyerApplication, Notification, Complaint
from .utils import (
    is_valid_uploaded_file,
    ALLOWED_GOV_ID_MIME_TYPES,
    ALLOWED_GOV_ID_EXTENSIONS,
    ALLOWED_PDF_MIME_TYPES,
    ALLOWED_PDF_EXTENSIONS,
)


def is_buyer(user):
    return user.groups.filter(name='Buyer').exists()


def mark_application_unavailable(application):
    if application.status not in ['Deleted', 'Paid']:
        application.status = 'Deleted'
        application.save()


def complaint_form(request):
    if not request.user.is_authenticated or not is_buyer(request.user):
        return redirect('error_access_denied')

    listing_id = request.GET.get('listing_id')
    listing = None

    if listing_id:
        listing = get_object_or_404(Listing, id=listing_id)

    if request.method == 'POST':
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        listing_id = request.POST.get('listing_id')

        listing = get_object_or_404(Listing, id=listing_id) if listing_id else None

        if not subject or not message:
            return render(request, 'interactions/complaint_submission.html', {
                'listing': listing,
                'error': 'Please fill in all required fields.'
            })

        Complaint.objects.create(
            reporter=request.user,
            reported_user=listing.seller if listing else None,
            listing=listing,
            subject=subject,
            message=message
        )

        return render(request, 'interactions/complaint_submission.html', {
            'success': 'Complaint submitted successfully.'
        })

    return render(request, 'interactions/complaint_submission.html', {
        'listing': listing
    })


@never_cache
def buyer_application_form(request, listing_id):
    if not request.user.is_authenticated or not is_buyer(request.user):
        return redirect('error_access_denied')

    listing = get_object_or_404(
        Listing,
        id=listing_id,
        is_active=True,
        is_sold=False
    )

    if not listing.is_approved or listing.approval_pending:
        return redirect('error_access_denied')

    if request.method == 'POST':
        existing_application = BuyerApplication.objects.filter(
            buyer=request.user,
            listing=listing
        ).exclude(
            status__in=['Deleted', 'RejectedByBuyer', 'RejectedBySeller']
        ).first()

        if existing_application:
            return render(request, 'interactions/buyer_application_form.html', {
                'listing': listing,
                'error': 'Application already submitted for this listing.'
            })

        first_name = request.POST.get('fname', '').strip()
        last_name = request.POST.get('lname', '').strip()
        email = request.POST.get('emailID', '').strip()

        gov_id = request.FILES.get('gov_id')
        mortgage_pre_approval = request.FILES.get('mortgage_pre_approval')
        bank_files = request.FILES.getlist('bank_statements')

        if not first_name or not last_name or not email:
            return render(request, 'interactions/buyer_application_form.html', {
                'listing': listing,
                'error': 'Please fill in all required text fields.'
            })

        if not gov_id:
            return render(request, 'interactions/buyer_application_form.html', {
                'listing': listing,
                'error': 'Government issued ID is required.'
            })

        if not is_valid_uploaded_file(
            gov_id,
            ALLOWED_GOV_ID_MIME_TYPES,
            ALLOWED_GOV_ID_EXTENSIONS
        ):
            return render(request, 'interactions/buyer_application_form.html', {
                'listing': listing,
                'error': 'Government issued ID must be a PNG, JPG, JPEG, or PDF file.'
            })

        if not mortgage_pre_approval:
            return render(request, 'interactions/buyer_application_form.html', {
                'listing': listing,
                'error': 'Mortgage pre-approval document is required.'
            })

        if not is_valid_uploaded_file(
            mortgage_pre_approval,
            ALLOWED_PDF_MIME_TYPES,
            ALLOWED_PDF_EXTENSIONS
        ):
            return render(request, 'interactions/buyer_application_form.html', {
                'listing': listing,
                'error': 'Mortgage pre-approval document must be a PDF file.'
            })

        for bank_file in bank_files:
            if not is_valid_uploaded_file(
                bank_file,
                ALLOWED_PDF_MIME_TYPES,
                ALLOWED_PDF_EXTENSIONS
            ):
                return render(request, 'interactions/buyer_application_form.html', {
                    'listing': listing,
                    'error': 'All bank statements must be PDF files.'
                })

        application = BuyerApplication.objects.create(
            buyer=request.user,
            seller=listing.seller,
            listing=listing,
            first_name=first_name,
            last_name=last_name,
            email=email,
            gov_id=gov_id,
            mortgage_pre_approval=mortgage_pre_approval,
            bank_statement_1=bank_files[0] if len(bank_files) > 0 else None,
            bank_statement_2=bank_files[1] if len(bank_files) > 1 else None,
            bank_statement_3=bank_files[2] if len(bank_files) > 2 else None,
            status='Pending'
        )

        Notification.objects.create(
            recipient=listing.seller,
            sender=request.user,
            title='New Buyer Application',
            message=f'{request.user.username} submitted an application for "{listing.title}".',
            application=application
        )

        return redirect('notifications_page')

    return render(request, 'interactions/buyer_application_form.html', {
        'listing': listing
    })


@never_cache
def buyer_payment(request, application_id):
    if not request.user.is_authenticated or not is_buyer(request.user):
        return redirect('error_access_denied')

    application = get_object_or_404(
        BuyerApplication.objects.select_related('listing', 'seller'),
        id=application_id,
        buyer=request.user
    )

    listing = application.listing

    if application.status == 'Paid':
        return redirect('purchase_success', application_id=application.id)

    def listing_is_unavailable():
        return (
            application.status == 'Deleted'
            or not listing.is_active
            or listing.is_sold
        )

    if listing_is_unavailable():
        mark_application_unavailable(application)

        return render(request, 'interactions/buyer_payment.html', {
            'application': application,
            'unavailable_message': 'Sorry, house no longer available.'
        })

    if request.method == 'POST':
        application.refresh_from_db()
        listing.refresh_from_db()

        if application.status == 'Paid':
            return redirect('purchase_success', application_id=application.id)

        if listing_is_unavailable():
            mark_application_unavailable(application)

            return render(request, 'interactions/buyer_payment.html', {
                'application': application,
                'unavailable_message': 'Sorry, house no longer available.'
            })

        application.status = 'Paid'
        application.save()

        listing.is_sold = True
        listing.is_active = False
        listing.save()

        # Remove purchased listing from every buyer's cart.
        SavedListing.objects.filter(listing=listing).delete()

        # Cancel all other in-process applications for this listing.
        BuyerApplication.objects.filter(
            listing=listing
        ).exclude(
            id=application.id
        ).exclude(
            status__in=['RejectedBySeller', 'RejectedByBuyer', 'Deleted', 'Paid']
        ).update(status='Deleted')

        Notification.objects.create(
            recipient=application.seller,
            sender=request.user,
            title='Buyer Completed Payment',
            message=f'The buyer completed payment for "{listing.title}".',
            application=application
        )

        Notification.objects.create(
            recipient=request.user,
            sender=application.seller,
            title='Purchase Complete',
            message=f'You successfully purchased "{listing.title}".',
            application=application
        )

        return redirect('purchase_success', application_id=application.id)

    return render(request, 'interactions/buyer_payment.html', {
        'application': application
    })


@never_cache
def buyer_application_decision(request, application_id):
    if not request.user.is_authenticated or not is_buyer(request.user):
        return redirect('error_access_denied')

    application = get_object_or_404(
        BuyerApplication.objects.select_related('listing', 'seller'),
        id=application_id,
        buyer=request.user
    )

    listing = application.listing

    if (
        application.status == 'Deleted'
        or not listing.is_active
        or listing.is_sold
    ):
        mark_application_unavailable(application)
        return redirect('buyer_payment', application_id=application.id)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'accept':
            application.status = 'AcceptedByBuyer'
            application.save()

            Notification.objects.create(
                recipient=application.seller,
                sender=request.user,
                title='Buyer Accepted Offer',
                message=f'The buyer accepted the offer for "{application.listing.title}".',
                application=application
            )

            return redirect('buyer_payment', application_id=application.id)

        elif action == 'reject':
            application.status = 'RejectedByBuyer'
            application.save()

            Notification.objects.create(
                recipient=application.seller,
                sender=request.user,
                title='Buyer Rejected Offer',
                message=f'The buyer rejected the accepted application for "{application.listing.title}".',
                application=application
            )

            return redirect('wishlist_page')

    return redirect('notifications_page')


@never_cache
def notifications_page(request):
    if not request.user.is_authenticated:
        return redirect('error_access_denied')

    notifications = Notification.objects.filter(
        recipient=request.user
    ).select_related(
        'application',
        'application__listing',
        'sender'
    ).order_by('-created_at')

    return render(request, 'interactions/notifications.html', {
        'notifications': notifications
    })


def mark_notification_read(request, notification_id):
    if not request.user.is_authenticated:
        return redirect('error_access_denied')

    notification = get_object_or_404(
        Notification,
        id=notification_id,
        recipient=request.user
    )
    notification.is_read = True
    notification.save()

    return redirect('notifications_page')


@never_cache
def purchase_success(request, application_id):
    if not request.user.is_authenticated or not is_buyer(request.user):
        return redirect('error_access_denied')

    application = get_object_or_404(
        BuyerApplication.objects.select_related('listing'),
        id=application_id,
        buyer=request.user
    )

    if application.status == 'Deleted':
        return render(request, 'interactions/buyer_payment.html', {
            'application': application,
            'unavailable_message': 'Sorry, house no longer available.'
        })

    if application.status != 'Paid':
        return redirect('notifications_page')

    return render(request, 'interactions/purchase_success.html', {
        'application': application
    })


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