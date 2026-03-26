from django.db import models


class Listing(models.Model):
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