from django.db import models
from django.contrib.auth.models import User
from listings.models import Listing


class Complaint(models.Model):
    reporter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='complaints_made'
    )
    reported_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='complaints_received',
        null=True,
        blank=True
    )
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return self.subject


class Notification(models.Model):
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_notifications'
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.recipient.username} - {self.title}"


class BuyerApplication(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('RejectedBySeller', 'Rejected By Seller'),
        ('AcceptedBySeller', 'Accepted By Seller'),
        ('RejectedByBuyer', 'Rejected By Buyer'),
        ('AcceptedByBuyer', 'Accepted By Buyer'),
        ('CounterSent', 'Counter Sent'),
        ('Deleted', 'Deleted'),
    ]

    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buyer_applications')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller_applications')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='applications')

    buyer_note = models.TextField(blank=True)
    offer_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    counter_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.buyer.username} -> {self.listing.title} ({self.status})"