from django.db import models
from django.contrib.auth.models import User


class BanRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ban_records')
    banned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bans_made')
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} banned by {self.banned_by.username}"


class ModerationHistory(models.Model):
    ACTION_CHOICES = [
        ('BAN_USER', 'Ban User'),
        ('UNBAN_USER', 'Unban User'),
        ('DELETE_LISTING', 'Delete Listing'),
        ('RESTORE_LISTING', 'Restore Listing'),
    ]

    admin_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='moderation_actions')
    target_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='moderation_targets')
    target_listing_title = models.CharField(max_length=255, blank=True)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.admin_user.username} - {self.action}"