# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('Buyer', 'Buyer'),
        ('Seller', 'Seller'),
        ('Admin', 'Admin'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40, blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='Buyer')
    login_status = models.BooleanField(default=False)
    seller_approved = models.BooleanField(default=False)
    seller_request_pending = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"