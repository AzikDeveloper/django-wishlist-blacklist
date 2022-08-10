from rest_framework import serializers
from .models import ModelBind
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from django.utils.encoding import smart_str
from django.apps import apps
from rest_framework.exceptions import ValidationError
from .utils import get_user_author


class ContentTypeField(serializers.RelatedField):
    default_error_messages = {
        'does_not_exist': _('Content type with model={value} does not exist.'),
        'invalid': _('Invalid value.'),
    }

    def __init__(self, **kwargs):
        kwargs.setdefault('queryset', ContentType.objects.all())
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        try:
            model = apps.get_model(data)
            return ContentType.objects.get_for_model(model)
        except LookupError:
            self.fail('does_not_exist', value=smart_str(data))
        except (TypeError, ValueError, AttributeError):
            self.fail('invalid')

    def to_representation(self, obj):
        return obj.pk


class _BinderSerializer(serializers.ModelSerializer):
    default_error_messages = {
        'does_not_exist': _('{model_name} with pk={pk} does not exist.'),
    }
    target_ct = ContentTypeField()

    class Meta:
        model = ModelBind
        fields = [
            "target_ct",
            "target_object_id",
            "type",
        ]

    def validate(self, attrs):
        #  TODO: create a custom field for target_object_id and move this validation to it?
        target_model = attrs["target_ct"].model_class()
        try:
            target_model.objects.get(pk=attrs["target_object_id"])
        except target_model.DoesNotExist:
            raise ValidationError({
                "target_object_id": self.error_messages['does_not_exist'].format(
                    model_name=target_model._meta.verbose_name.capitalize(),
                    pk=attrs["target_object_id"]
                )
            })
        return super().validate(attrs)


class WishlistStateSerializerMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        author = get_user_author(self.context["request"].user)
        if not hasattr(author, "get_wishlists"):
            raise Exception(
                f"{author.__class__.__name__} object does not have get_wishlists method. "
                "Did you forget to inherit from binder.models.WishlistModelMixin?"
            )
        self.fields["is_wishlisted"] = serializers.SerializerMethodField()
        self._wishlists = list(author.get_wishlists(self.get_serializer_model()).values_list("pk", flat=True))

    def get_serializer_model(self):
        return self.Meta.model

    def get_is_wishlisted(self, obj):
        return obj.pk in self._wishlists


class BlacklistStateModelSerializerMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        author = get_user_author(self.context["request"].user)
        if not hasattr(author, "get_blacklists"):
            raise Exception(
                f"{author.__class__.__name__} object does not have get_blacklists method. "
                "Did you forget to inherit from binder.models.BlacklistModelMixin?"
            )
        self.fields["is_blacklisted"] = serializers.SerializerMethodField()
        self._blacklists = list(author.get_blacklists(self.get_serializer_model()).values_list("pk", flat=True))

    def get_serializer_model(self):
        return self.Meta.model

    def get_is_blacklisted(self, obj):
        return obj.pk in self._blacklists


class WishlistStateModelSerializer(WishlistStateSerializerMixin, serializers.ModelSerializer):

    def get_serializer_model(self):
        return self.Meta.model


class BlacklistStateModelSerializer(BlacklistStateModelSerializerMixin, serializers.ModelSerializer):

    def get_serializer_model(self):
        return self.Meta.model


__all__ = ['WishlistStateSerializerMixin', 'WishlistStateModelSerializer', '_BinderSerializer']
