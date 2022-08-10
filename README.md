# django-wishlist-blacklist

### Easily manage blacklist and wishlist in your Django project.



## Installation

```bash
pip install django-wishlist-blacklist (soon in pip)
```
Add `django_wishlist_blacklist` to your INSTALLED_APPS:

```python
INSTALLED_APPS = [
    ...
    'django_wishlist_blacklist',
    ...
]
```

## Usage:

Inherit from `django_wishlist_blacklist.models.WishlistAuthorModelMixin` or
`django_wishlist_blacklist.models.BlacklistAuthorModelMixin` in your User model:

```python
class User(WishlistAuthorModelMixin, BlacklistAuthorModelMixin, AbstractUser)
    pass
```

## Usage Example

```pycon
>>> product = Product.objects.first()
>>> user.is_wishlisted(product)
False
>>> user.add_to_wishlist(product)
<ModelBind: Casey Gates -> Ball(7)>
>>> user.is_wishlisted(product)
True
>>> user.get_wishlists(Product)
<QuerySet [<Ball: Ball(7)>]>
>>> user.remove_from_wishlist(product)
>>> user.get_wishlists(Product)
<QuerySet []>
```

## Ready API for blacklisting and wishlisting

Add `django_wishlist_blacklist.urls` to your URL patterns:

```python
urlpatterns = [
    ...
    url(r'^wishlist-blacklist/', include('django_wishlist_blacklist.urls')),
    ...
]
```

### Example to add product to wishlist:

`POST /wishlist-blacklist/add/`

```json
 {
  "target_ct": "product.Product",
  "target_object_id": 9,
  "type": "wishlist"
}
```

### Example to remove product from wishlist:

`POST /wishlist-blacklist/remove/`

```json
 {
  "target_ct": "product.Product",
  "target_object_id": 9,
  "type": "wishlist"
}
```       

## Base serializer for appending `is_wishlisted` and `is_blacklisted` fields to serializer

```python
from django_wishlist_blacklist.serializers import WishlistStateModelSerializer


class ProductSerializer(WishlistStateModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'brand', 'created_at')
```

```pycon
>>> serializer = ProductSerializer(product, context={'request': request})
>>> serializer.data
[
    {
        "id": 6,
        "name": "Ball",
        "brand": "Ball",
        "created_at": "2020-01-01T00:00:00Z",
        "is_wishlisted": True,
    },
    {
        "id": 7,
        "name": "Ball",
        "brand": "Ball",
        "created_at": "2020-01-01T00:00:00Z",
        "is_wishlisted": False,
    }
]
```
