from django.contrib import admin

from .models import Wishlist, Blacklist


class BaseModelBinderAdmin(admin.ModelAdmin):
    list_display = ['author', 'target']
    list_filter = ['created_at']
    search_fields = ['author', 'target']


@admin.register(Wishlist)
class WishlistAdmin(BaseModelBinderAdmin):
    pass


@admin.register(Blacklist)
class BlacklistAdmin(BaseModelBinderAdmin):
    pass
