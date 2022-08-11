from rest_framework import serializers
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


class _BinderSerializer(serializers.Serializer):
    default_error_messages = {
        'does_not_exist': _('{model_name} with pk={pk} does not exist.'),
    }
    target_ct = ContentTypeField()
    target_object_id = serializers.CharField()

    def validate(self, attrs):
        target_model = attrs["target_ct"].model_class()
        try:
            target = target_model._default_manager.get(pk=attrs["target_object_id"])
        except target_model.DoesNotExist:
            raise ValidationError({
                "target_object_id": self.error_messages['does_not_exist'].format(
                    model_name=target_model._meta.verbose_name.capitalize(),
                    pk=attrs["target_object_id"]
                )
            })
        attrs.update({"target": target})
        return attrs


"""PUBLIC API STARTS HERE"""


class WishlistStateSerializerMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        author = get_user_author(self.context["request"].user)
        self.fields["is_wishlisted"] = serializers.SerializerMethodField()
        self._wishlists = list(
            author.get_wishlists(self.Meta.model).values_list("target_object_id", flat=True)
        )

    def get_is_wishlisted(self, obj):
        return obj.pk in self._wishlists


class BlacklistStateModelSerializerMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        author = get_user_author(self.context["request"].user)
        self.fields["is_blacklisted"] = serializers.SerializerMethodField()
        self._blacklists = list(
            author.get_blacklists(self.Meta.model).values_list("target_object_id", flat=True)
        )

    def get_is_blacklisted(self, obj):
        return obj.pk in self._blacklists


__all__ = ['WishlistStateSerializerMixin', 'BlacklistStateModelSerializerMixin', '_BinderSerializer']
