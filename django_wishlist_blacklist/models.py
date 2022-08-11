from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.utils.translation import gettext_lazy as _


class BaseModelBinder(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    # author content type
    author_object_id = models.PositiveIntegerField()
    author = GenericForeignKey(ct_field="author_content_type", fk_field="author_object_id")

    # target content type
    target_object_id = models.PositiveIntegerField()
    target = GenericForeignKey(fk_field="target_object_id", ct_field="target_content_type")

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.author} -> {self.target}"


class Wishlist(BaseModelBinder):
    author_content_type = models.ForeignKey(
        ContentType,
        related_name="author_wishlists",
        on_delete=models.CASCADE,
    )
    target_content_type = models.ForeignKey(
        ContentType,
        related_name="target_wishlists",
        on_delete=models.CASCADE,
    )

    class Meta:
        unique_together = (
            'author_content_type', 'author_object_id',
            'target_content_type', 'target_object_id',
        )
        verbose_name = _("wishlist")
        verbose_name_plural = _("wishlists")


class Blacklist(BaseModelBinder):
    author_content_type = models.ForeignKey(
        ContentType,
        related_name="author_blacklists",
        on_delete=models.CASCADE,
    )
    target_content_type = models.ForeignKey(
        ContentType,
        related_name="target_blacklists",
        on_delete=models.CASCADE,
    )

    class Meta:
        unique_together = (
            'author_content_type', 'author_object_id',
            'target_content_type', 'target_object_id',
        )
        verbose_name = _("blacklist")
        verbose_name_plural = _("blacklists")


class WishlistAuthorModel(models.Model):
    my_wishlists = GenericRelation(Wishlist, related_query_name="wishlisted_by", object_id_field="author_object_id",
                                   content_type_field="author_content_type")

    class Meta:
        abstract = True

    def is_wishlisted(self, obj):
        self._check_model_is_wishlist_target(obj.__class__)
        return self.my_wishlists.filter(
            target_object_id=obj.pk,
            target_content_type=ContentType.objects.get_for_model(obj),
        ).exists()

    def add_to_wishlist(self, obj):
        self._check_model_is_wishlist_target(obj.__class__)
        return self.my_wishlists.create(
            target_content_type=ContentType.objects.get_for_model(obj),
            target_object_id=obj.pk
        )

    def remove_from_wishlist(self, obj):
        self._check_model_is_wishlist_target(obj.__class__)
        return self.my_wishlists.filter(
            target_content_type=ContentType.objects.get_for_model(obj),
            target_object_id=obj.pk
        ).delete()

    def get_wishlists(self, model):
        self._check_model_is_wishlist_target(model)
        return self.my_wishlists.filter(
            target_content_type=ContentType.objects.get_for_model(model)
        )

    def _check_model_is_wishlist_target(self, model):
        if not issubclass(model, WishlistTargetModel):
            raise TypeError(
                f"{model.__name__} cannot be used as a wishlist item. "
                "Did you forget to inherit from WishlistTargetModel?"
            )


class WishlistTargetModel(models.Model):
    target_wishlists = GenericRelation(
        Wishlist,
        object_id_field="target_object_id",
        content_type_field="target_content_type"
    )

    class Meta:
        abstract = True


class BlacklistAuthorModel(models.Model):
    my_blacklists = GenericRelation(Blacklist, related_query_name="blacklisted_by", object_id_field="author_object_id",
                                    content_type_field="author_content_type")

    class Meta:
        abstract = True

    def is_blacklisted(self, obj):
        self._check_model_is_blacklist_target(obj.__class__)
        return self.my_blacklists.filter(
            target_object_id=obj.pk,
            target_content_type=ContentType.objects.get_for_model(obj),
        ).exists()

    def add_to_blacklist(self, obj):
        self._check_model_is_blacklist_target(obj.__class__)
        return self.my_blacklists.create(
            target_content_type=ContentType.objects.get_for_model(obj),
            target_object_id=obj.pk
        )

    def remove_from_blacklist(self, obj):
        self._check_model_is_blacklist_target(obj.__class__)
        return self.my_blacklists.filter(
            target_content_type=ContentType.objects.get_for_model(obj),
            target_object_id=obj.pk
        ).delete()

    def get_blacklists(self, model):
        self._check_model_is_blacklist_target(model)
        return self.my_blacklists.filter(
            target_content_type=ContentType.objects.get_for_model(model)
        )

    def _check_model_is_blacklist_target(self, model):
        if not issubclass(model, BlacklistTargetModel):
            raise TypeError(
                f"{model.__name__} cannot be used as a blacklist item. "
                "Did you forget to inherit from BlacklistTargetModel?"
            )


class BlacklistTargetModel(models.Model):
    target_blacklists = GenericRelation(
        Blacklist,
        object_id_field="target_object_id",
        content_type_field="target_content_type"
    )

    class Meta:
        abstract = True


__all__ = ['Wishlist', 'Blacklist', 'WishlistAuthorModel', 'WishlistTargetModel', 'BlacklistAuthorModel',
           'BlacklistTargetModel']
