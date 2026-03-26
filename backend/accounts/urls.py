from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_bearer, name='home'),
    path('login/', views.login_bearer, name='loginPage'),
    path('register/', views.register_page, name='registerPage'),
    path('admin-create-account/', views.admin_create_account, name='adminCreateAccount'),
    path('buyer/', views.buyer_page, name='buyer_page'),
    path('seller/', views.seller_page, name='seller_page'),
    path('admin-home/', views.admin_page, name='adminHome'),
    path('profile/', views.buyer_manageprofile, name='buyer_manageprofile'),
    path('logout/', views.logout_bearer, name='logoutPage'),
]