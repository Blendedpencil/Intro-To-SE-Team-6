from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_bearer, name='loginPage'),
    path('register/', views.register_page, name='registerPage'),

    path('seller/login/', views.seller_login_page, name='seller_login_page'),
    path('seller/register/', views.seller_register_page, name='seller_register_page'),
    path('seller/profile/', views.seller_manage_profile, name='seller_manage_profile'),

    path('admin-create-account/', views.admin_create_account, name='adminCreateAccount'),

    path('seller/', views.seller_page, name='seller_page'),
    path('admin-home/', views.admin_page, name='adminHome'),

    path('profile/', views.buyer_manageprofile, name='buyer_manageprofile'),
    path('logout/', views.logout_bearer, name='logoutPage'),
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),
]