from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.admin_login_page, name='admin_login_page'),
    path('create-account/', views.admin_create_account_page, name='admin_create_account_page'),
    path('home/', views.admin_home, name='admin_home'),
    path('ban-user/', views.admin_ban_user, name='admin_ban_user'),
    path('manage-profile/', views.admin_manage_profile, name='admin_manage_profile'),
    path('report/<int:complaint_id>/', views.admin_report_detail, name='admin_report_detail'),
    path('search-user/', views.admin_search_user, name='admin_search_user'),
    path('approve-seller/<int:user_id>/', views.approve_seller_request, name='approve_seller_request'),
    path('reject-seller/<int:user_id>/', views.reject_seller_request, name='reject_seller_request'),
    path('delete-listing/<int:listing_id>/', views.admin_delete_listing, name='admin_delete_listing'),
    path('moderation-history/', views.admin_moderation_history, name='admin_moderation_history'),
]