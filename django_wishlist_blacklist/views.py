from rest_framework import generics
from .models import Wishlist, Blacklist
from .utils import get_user_author
from rest_framework.response import Response
from rest_framework import status
from .serializers import BinderSerializer
from rest_framework.exceptions import ValidationError
from django.db.utils import IntegrityError
from rest_framework.permissions import IsAuthenticated


class BaseModelBinderView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = BinderSerializer

    allowed_actions = ["add", "remove"]
    binder_class = None

    def remove(self, author, target_ct, target_pk):
        is_deleted, bind = author._delete_bind(self.binder_class, ct=target_ct, pk=target_pk)
        if is_deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def add(self, author, target_ct, target_pk):
        try:
            author._create_bind(self.binder_class, ct=target_ct, pk=target_pk)
        except IntegrityError:
            return Response(status=status.HTTP_409_CONFLICT)
        else:
            return Response(status=status.HTTP_201_CREATED)

    def get_action_handler(self, action: str):
        if action.lower() in self.allowed_actions:
            return getattr(self, action.lower())
        else:
            raise ValidationError(f"Action {action} is not allowed. Allowed actions: {self.allowed_actions}")

    def post(self, request, action):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action_handler = self.get_action_handler(action)
        author = get_user_author(request.user)
        return action_handler(
            author,
            serializer.validated_data["target_ct"],
            serializer.validated_data["target_object_id"],
        )


class WishlistView(BaseModelBinderView):
    binder_class = Wishlist


class BlacklistView(BaseModelBinderView):
    binder_class = Blacklist


__all__ = ['WishlistView', 'BlacklistView']
