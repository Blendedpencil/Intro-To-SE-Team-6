from django.contrib import admin
from .models import BanRecord, ModerationHistory

admin.site.register(BanRecord)
admin.site.register(ModerationHistory)