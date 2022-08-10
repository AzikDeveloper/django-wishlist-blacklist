from .views import WishlistBlacklistView
from django.urls import path

app_name = "binder"
urlpatterns = [
    path('<str:action>/', WishlistBlacklistView.as_view(), name='binder'),
]
