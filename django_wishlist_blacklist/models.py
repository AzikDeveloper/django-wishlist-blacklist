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


class WishlistAuthorModelMixin(models.Model):
    my_wishlists = GenericRelation(Wishlist, related_query_name="wishlisted_by", object_id_field="author_object_id",
                                   content_type_field="author_content_type")

    class Meta:
        abstract = True

    def is_wishlisted(self, obj):
        return self.my_wishlists.filter(
            target_object_id=obj.pk,
            target_content_type=ContentType.objects.get_for_model(obj),
        ).exists()

    def add_to_wishlist(self, obj):
        return self.my_wishlists.create(
            target_content_type=ContentType.objects.get_for_model(obj),
            target_object_id=obj.pk
        )

    def remove_from_wishlist(self, obj):
        return self.my_wishlists.filter(
            target_content_type=ContentType.objects.get_for_model(obj),
            target_object_id=obj.pk
        ).delete()

    def get_wishlists(self, model):
        return self.my_wishlists.filter(
            target_content_type=ContentType.objects.get_for_model(model)
        )


class BlacklistAuthorModelMixin(models.Model):
    my_blacklists = GenericRelation(Blacklist, related_query_name="blacklisted_by", object_id_field="author_object_id",
                                    content_type_field="author_content_type")

    class Meta:
        abstract = True

    def is_blacklisted(self, obj):
        return self.my_blacklists.filter(
            target_object_id=obj.pk,
            target_content_type=ContentType.objects.get_for_model(obj),
        ).exists()

    def add_to_blacklist(self, obj):
        return self.my_blacklists.create(
            target_content_type=ContentType.objects.get_for_model(obj),
            target_object_id=obj.pk
        )

    def remove_from_blacklist(self, obj):
        return self.my_blacklists.filter(
            target_content_type=ContentType.objects.get_for_model(obj),
            target_object_id=obj.pk
        ).delete()

    def get_blacklists(self, model):
        return self.my_blacklists.filter(
            target_content_type=ContentType.objects.get_for_model(model)
        )


__all__ = ['Wishlist', 'Blacklist', 'WishlistAuthorModelMixin', 'BlacklistAuthorModelMixin']
