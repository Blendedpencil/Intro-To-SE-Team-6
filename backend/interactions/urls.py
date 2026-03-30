from django.urls import path
from . import views

urlpatterns = [
    path('complaint/', views.complaint_form, name='complaint_form'),
    path('apply/<int:listing_id>/', views.buyer_application_form, name='buyer_application_form'),
    path('payment/<int:application_id>/', views.buyer_payment, name='buyer_payment'),
    path('application-decision/<int:application_id>/', views.buyer_application_decision, name='buyer_application_decision'),
    path('notifications/', views.notifications_page, name='notifications_page'),
    path('notifications/read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('purchase-success/<int:application_id>/', views.purchase_success, name='purchase_success'),
]