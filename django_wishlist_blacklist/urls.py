from .views import WishlistView, BlacklistView
from django.urls import path

urlpatterns = [
    path('wishlist/<str:action>/', WishlistView.as_view(), name='wishlist'),
    path('blacklist/<str:action>/', BlacklistView.as_view(), name='blacklist'),
]
