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

    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True
    )

    phone = models.CharField(max_length=30, blank=True)
    bio = models.TextField(blank=True)

    deleted_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class UserReview(models.Model):
    THUMBS_UP = 'UP'
    THUMBS_DOWN = 'DOWN'

    VOTE_CHOICES = [
        (THUMBS_UP, 'Thumbs Up'),
        (THUMBS_DOWN, 'Thumbs Down'),
    ]

    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='profile_reviews_given'
    )

    reviewed_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='profile_reviews_received'
    )

    vote = models.CharField(max_length=4, choices=VOTE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('reviewer', 'reviewed_user')

    def __str__(self):
        return f"{self.reviewer.username} reviewed {self.reviewed_user.username}: {self.vote}"