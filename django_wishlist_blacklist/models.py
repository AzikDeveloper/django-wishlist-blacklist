from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.utils.translation import gettext_lazy as _


class ModelBinder(models.Model):
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


class Wishlist(ModelBinder):
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


class Blacklist(ModelBinder):
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


class BaseAuthorModelMixin:

    def _check_existence(self, binder_class, obj):
        return binder_class.objects.filter(
            author_object_id=self.pk,
            author_content_type=ContentType.objects.get_for_model(self),
            target_object_id=obj.pk,
            target_content_type=ContentType.objects.get_for_model(obj),
        ).exists()

    def _create_bind(self, binder_class, obj=None, ct=None, pk=None):
        if ct and pk:
            binder_class.objects.create(
                author_object_id=self.pk,
                author_content_type=ContentType.objects.get_for_model(self),
                target_object_id=pk,
                target_content_type=ct,
            )
        elif obj:
            return binder_class.objects.create(
                author_object_id=self.pk,
                author_content_type=ContentType.objects.get_for_model(self),
                target_object_id=obj.pk,
                target_content_type=ContentType.objects.get_for_model(obj),
            )

    def _delete_bind(self, binder_class, obj=None, ct=None, pk=None):
        if ct and pk:
            bind = binder_class.objects.filter(
                author_object_id=self.pk,
                author_content_type=ContentType.objects.get_for_model(self),
                target_object_id=pk,
                target_content_type=ct,
            ).first()
        elif obj:
            bind = binder_class.objects.filter(
                author_object_id=self.pk,
                author_content_type=ContentType.objects.get_for_model(self),
                target_object_id=obj.pk,
                target_content_type=ContentType.objects.get_for_model(obj),
            ).first()
        else:
            raise ValueError("Either obj or ct and pk must be provided")
        if bind:
            bind.delete()
            return True, bind
        return False, None

    def _my_binds(self, binder_class, model):
        return binder_class.objects.filter(
            author_object_id=self.pk,
            author_content_type=ContentType.objects.get_for_model(self),
            target_content_type=ContentType.objects.get_for_model(model),
        )


class WishlistAuthorModelMixin(BaseAuthorModelMixin, models.Model):
    my_wishlists = GenericRelation(Wishlist, related_query_name="wishlisted_by")

    class Meta:
        abstract = True

    def is_wishlisted(self, obj):
        return self._check_existence(Wishlist, obj)

    def add_to_wishlist(self, obj):
        return self._create_bind(Wishlist, obj)

    def remove_from_wishlist(self, obj):
        return self._delete_bind(Wishlist, obj)

    def get_wishlists(self, model):
        return self._my_binds(Wishlist, model)


class BlacklistAuthorModelMixin(BaseAuthorModelMixin, models.Model):
    my_blacklists = GenericRelation(Blacklist, related_query_name="blacklisted_by")

    class Meta:
        abstract = True

    def is_blacklisted(self, obj):
        return self._check_existence(Blacklist, obj)

    def add_to_blacklist(self, obj):
        return self._create_bind(Blacklist, obj)

    def remove_from_blacklist(self, obj):
        return self._delete_bind(Blacklist, obj)

    def get_blacklists(self, model):
        return self._my_binds(Blacklist, model)


__all__ = ['Wishlist', 'Blacklist', 'WishlistAuthorModelMixin', 'BlacklistAuthorModelMixin']
