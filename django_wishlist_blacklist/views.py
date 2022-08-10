from rest_framework import generics
from .models import ModelBind
from .utils import get_user_author
from rest_framework.response import Response
from rest_framework import status
from .serializers import _BinderSerializer
from rest_framework.exceptions import ValidationError
from django.db.utils import IntegrityError
from rest_framework.permissions import IsAuthenticated
from django.contrib.contenttypes.models import ContentType
from .signals import (
    post_add_to_wishlist,
    post_remove_from_wishlist,
    post_add_to_blacklist,
    post_remove_from_blacklist,
)


class WishlistBlacklistActionMixin:
    allowed_actions = ["add", "remove"]

    @staticmethod
    def remove(request, _type, target_ct, target_pk):
        author = get_user_author(request.user)
        bind = ModelBind.objects.filter(
            author_content_type=ContentType.objects.get_for_model(author),
            author_object_id=author.pk,
            target_content_type=target_ct,
            target_object_id=target_pk,
            type=_type,
        ).first()
        if bind:
            bind.delete()
            if _type == ModelBind.TypeChoices.WISHLIST:
                post_remove_from_wishlist.send(sender=ModelBind, instance=bind)
            elif _type == ModelBind.TypeChoices.BLACKLIST:
                post_remove_from_blacklist.send(sender=ModelBind, instance=bind)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def add(request, _type, target_ct, target_pk):
        author = get_user_author(request.user)
        try:
            bind = ModelBind.objects.create(
                author_content_type=ContentType.objects.get_for_model(author),
                author_object_id=author.pk,
                target_content_type=target_ct,
                target_object_id=target_pk,
                type=_type,
            )
        except IntegrityError:
            return Response(status=status.HTTP_409_CONFLICT)
        else:
            if _type == ModelBind.TypeChoices.WISHLIST:
                post_add_to_wishlist.send(sender=ModelBind, instance=bind)
            elif _type == ModelBind.TypeChoices.BLACKLIST:
                post_add_to_blacklist.send(sender=ModelBind, instance=bind)
            return Response(status=status.HTTP_201_CREATED)

    def get_action_handler(self, action: str):
        if action.lower() in self.allowed_actions:
            return getattr(self, action)
        else:
            raise ValidationError(f"Action {action} is not allowed. Allowed actions: {self.allowed_actions}")


class WishlistBlacklistView(WishlistBlacklistActionMixin, generics.GenericAPIView):
    """
      Add/remove object from/to wishlist/blacklist
        type - type of action ("wishlist" or "blacklist")
        target_ct - content type of target object. Example: "app_name.ModelName"
        target_pk - pk of target object which will be added/removed from/to wishlist/blacklist

        "author_ct" and "author_pk" are automatically set to current user. If you want to use another related field,
        then you can provide a "get_binder_author" method in your user model.

        Example to add product to wishlist:
        POST .../add/
        {
          "target_ct": "product.Product",
          "target_object_id": 9,
          "type": "wishlist"
        }
        Example to remove product from wishlist:
        POST .../remove/
        {
          "target_ct": "product.Product",
          "target_object_id": 9,
          "type": "wishlist"
        }
    """
    serializer_class = _BinderSerializer
    permission_classes = [IsAuthenticated]
    allowed_actions = ["add", "remove"]

    def post(self, request, action):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action_handler = self.get_action_handler(action)
        return action_handler(
            request,
            serializer.validated_data["type"],
            serializer.validated_data["target_ct"],
            serializer.validated_data["target_object_id"],
        )


__all__ = ['WishlistBlacklistView', 'WishlistBlacklistActionMixin']
