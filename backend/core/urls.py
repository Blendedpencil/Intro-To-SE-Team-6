from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('contact/', views.contact_page, name='contact_page'),
    path('error/access-denied/', views.error_access_denied, name='error_access_denied'),
]