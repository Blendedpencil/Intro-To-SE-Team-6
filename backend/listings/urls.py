from django.urls import path
from . import views

urlpatterns = [
    path('buyer/', views.buyer_page, name='buyer_page'),
    path('details/', views.buyer_subpage, name='buyer_subpage'),
    path('compare/', views.comparison_page, name='comparison_page'),
    path('wishlist/', views.wishlist_page, name='wishlist_page'),
    path('create/', views.create_listing, name='create_listing'),
]