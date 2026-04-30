from django.db import models
from django.contrib.auth.models import User


class Listing(models.Model):
    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='listings',
        blank=True,
        null=True
    )
    title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    style = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    image = models.ImageField(upload_to='listing_images/', blank=True, null=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_on = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title


class Order(models.Model):
    listing = models.ForeignKey(
        Listing,
        on_delete=models.SET_NULL,
        related_name='orders',
        blank=True,
        null=True
    )
    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders_to_fulfill',
        blank=True,
        null=True
    )
    product_name = models.CharField(max_length=200)
    ship_to_address = models.TextField()
    placed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-placed_at']

    def __str__(self):
        return f"{self.product_name} order placed at {self.placed_at}"
