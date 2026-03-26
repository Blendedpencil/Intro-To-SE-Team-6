from django.contrib import admin

# Register your models here.
from .models import Complaint, Notification

admin.site.register(Complaint)
admin.site.register(Notification)