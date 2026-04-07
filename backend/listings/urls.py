from django.urls import path
from . import views

urlpatterns = [
    path('buyer/', views.buyer_page, name='buyer_page'),
    path('details/<int:listing_id>/', views.listing_details, name='listing_details'),
    path('wishlist/', views.wishlist_page, name='wishlist_page'),
    path('save/<int:listing_id>/', views.save_listing, name='save_listing'),
    path('remove-saved/<int:listing_id>/', views.remove_saved_listing, name='remove_saved_listing'),
    path('compare/', views.comparison_page, name='comparison_page'),

    path('create/', views.create_listing, name='create_listing'),
    path('seller/dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('seller/edit/', views.seller_edit_listing, name='seller_edit_listing'),
    path('seller/negotiation/', views.seller_negotiation, name='seller_negotiation'),
]