from django.urls import path
from . import views

urlpatterns = [
    path('notifications/', views.notifications_page, name='notifications_page'),
    path('notifications/read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('complaint/', views.complaint_form, name='complaint_form'),
    path('notify-seller/', views.notify_seller, name='notify_seller'),
]