from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.utils.translation import gettext_lazy as _


class ModelBind(models.Model):
    class TypeChoices(models.TextChoices):
        WISHLIST = 'wishlist', _("saqlash")
        BLACKLIST = 'blacklist', _("qora ro`yxat")

    type = models.CharField(max_length=50, verbose_name=_('Tip'), choices=TypeChoices.choices)

    # author content type
    author_content_type = models.ForeignKey(
        ContentType,
        related_name="author_binds",
        on_delete=models.CASCADE,
    )
    author_object_id = models.PositiveIntegerField()
    author = GenericForeignKey(ct_field="author_content_type", fk_field="author_object_id")

    # target content type
    target_content_type = models.ForeignKey(
        ContentType,
        related_name="target_binds",
        on_delete=models.CASCADE,
    )
    target_object_id = models.PositiveIntegerField()
    target = GenericForeignKey(fk_field="target_object_id", ct_field="target_content_type")

    class Meta:
        unique_together = (
            'author_content_type', 'author_object_id',
            'target_content_type', 'target_object_id',
            'type',
        )
        verbose_name = _("model bind")
        verbose_name_plural = _("model binds")

    def __str__(self):
        return f"{self.author} -> {self.target}"


class WishlistAuthorModelMixin(models.Model):
    class Meta:
        abstract = True

    def is_wishlisted(self, obj):
        return ModelBind.objects.filter(
            author_object_id=self.pk,
            author_content_type=ContentType.objects.get_for_model(self),
            target_object_id=obj.pk,
            target_content_type=ContentType.objects.get_for_model(obj),
            type=ModelBind.TypeChoices.WISHLIST,
        ).exists()

    def add_to_wishlist(self, obj):
        bind = ModelBind.objects.create(
            author_object_id=self.pk,
            author_content_type=ContentType.objects.get_for_model(self),
            target_object_id=obj.pk,
            target_content_type=ContentType.objects.get_for_model(obj),
            type=ModelBind.TypeChoices.WISHLIST,
        )
        return bind

    def remove_from_wishlist(self, obj):
        ModelBind.objects.filter(
            author_object_id=self.pk,
            author_content_type=ContentType.objects.get_for_model(self),
            target_object_id=obj.pk,
            target_content_type=ContentType.objects.get_for_model(obj),
            type=ModelBind.TypeChoices.WISHLIST,
        ).delete()

    def get_wishlists(self, model):
        return model._default_manager.filter(
            pk__in=ModelBind.objects.filter(
                author_object_id=self.pk,
                author_content_type=ContentType.objects.get_for_model(self),
                target_content_type=ContentType.objects.get_for_model(model),
                type=ModelBind.TypeChoices.WISHLIST,
            ).values_list("target_object_id", flat=True)
        )


class BlacklistAuthorModelMixin(models.Model):
    class Meta:
        abstract = True

    def is_blacklisted(self, obj):
        return ModelBind.objects.filter(
            author_object_id=self.pk,
            author_content_type=ContentType.objects.get_for_model(self),
            target_object_id=obj.pk,
            target_content_type=ContentType.objects.get_for_model(obj),
            type=ModelBind.TypeChoices.BLACKLIST,
        ).exists()

    def add_to_blacklist(self, obj):
        bind = ModelBind.objects.create(
            author_object_id=self.pk,
            author_content_type=ContentType.objects.get_for_model(self),
            target_object_id=obj.pk,
            target_content_type=ContentType.objects.get_for_model(obj),
            type=ModelBind.TypeChoices.BLACKLIST,
        )
        return bind

    def remove_from_blacklist(self, obj):
        ModelBind.objects.filter(
            author_object_id=self.pk,
            author_content_type=ContentType.objects.get_for_model(self),
            target_object_id=obj.pk,
            target_content_type=ContentType.objects.get_for_model(obj),
            type=ModelBind.TypeChoices.BLACKLIST,
        ).delete()

    def get_blacklists(self, model):
        return model._default_manager.filter(
            pk__in=ModelBind.objects.filter(
                author_object_id=self.pk,
                author_content_type=ContentType.objects.get_for_model(self),
                target_content_type=ContentType.objects.get_for_model(model),
                type=ModelBind.TypeChoices.BLACKLIST,
            ).values_list("target_object_id", flat=True)
        )


__all__ = ['ModelBind', 'WishlistAuthorModelMixin', 'BlacklistAuthorModelMixin']
