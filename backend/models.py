from django.db import models

class Users(models.Model):
    FirstName = models.CharField(max_length=30)
    LastName = models.CharField(max_length=30)
    id = models.BigIntegerField()
    password = models.BinaryField()
    loginStatus = models.BooleanField()
    published_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Buyers(models.Model):
    id = models.BigIntegerField()
    

    def __str__(self):
        return self.title


class Sellers(models.Model):
    id = models.BigIntegerField()
    published_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Admins(models.Model):
    id = models.BigIntegerField()
    published_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Reports(models.Model):
    id = models.BigIntegerField()
    published_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Listings(models.Model):
    id = models.BigIntegerField()
    published_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Saved_Listings(models.Model):
    id = models.BigIntegerField()
    published_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Applications(models.Model):
    id = models.BigIntegerField()
    published_at = models.DateTimeField(auto_now_add=True)
    bargained_price = models.IntegerField()
    document = models.FileField()
    buyer = models.ForeignKey(Buyers, on_delete=models.CASCADE)
    seller = models.ForeignKey(Sellers, on_delete=models.CASCADE)
    initial_notes_buyer = models.CharField(max_length=400)

    accepted_by_seller = models.BooleanField()
    rejection_notes_seller = models.CharField(max_length=400)
    seller_rejected_on = models.DateField()
    seller_accepted_on = models.DateField()
    accepted_by_buyer = models.BooleanField()
    rejection_notes_buyer = models.BooleanField()
    buyer_rejected_on = models.DateField()
    buyer_accepted_on = models.DateField()
    
    





    def __str__(self):
        return self.title
    

