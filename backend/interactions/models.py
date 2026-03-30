from django.db import models
from django.contrib.auth.models import User
from listings.models import Listing
# Create your models here.



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

class Payment(models.Model):
    id = models.BigIntegerField(primary_key=True)
    listing = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='listing'
    )
    buyer = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='buyer'
    )
    cardNumber = models.IntegerField()
    cardEXP = models.IntegerField()
    cardSecurityCode = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.buyer.username} - {self.title}"
