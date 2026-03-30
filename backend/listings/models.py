from django.db import models
from django.contrib.auth.models import User


class Listing(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    location = models.CharField(max_length=200)
    style = models.CharField(max_length=100, default='Other')
    description = models.TextField()

    bedrooms = models.PositiveIntegerField(default=0)
    bathrooms = models.PositiveIntegerField(default=0)
    square_footage = models.PositiveIntegerField(default=0)

    image = models.ImageField(upload_to='listing_images/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_sold = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class SavedListing(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_listings')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('buyer', 'listing')

    def __str__(self):
        return f"{self.buyer.username} saved {self.listing.title}"