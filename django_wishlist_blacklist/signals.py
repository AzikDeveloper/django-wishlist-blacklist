from django.dispatch import Signal

post_add_to_wishlist = Signal()
post_remove_from_wishlist = Signal()

post_add_to_blacklist = Signal()
post_remove_from_blacklist = Signal()
