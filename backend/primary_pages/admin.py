from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'login_status', 'deleted_on')
    search_fields = ('user__username', 'user__email', 'role')
    list_filter = ('role', 'login_status')