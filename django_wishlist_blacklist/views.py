from rest_framework import generics
from .utils import get_user_author
from rest_framework.response import Response
from rest_framework import status
from .serializers import _BinderSerializer
from rest_framework.exceptions import ValidationError
from django.db.utils import IntegrityError
from rest_framework.permissions import IsAuthenticated


class BaseModelBinderView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = _BinderSerializer

    @staticmethod
    def add_bind(author, target):
        raise NotImplementedError()

    @staticmethod
    def remove_bind(author, target):
        raise NotImplementedError()

    def post(self, request, action):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        target = serializer.validated_data["target"]

        author = get_user_author(request.user)

        if action == "add":
            try:
                self.add_bind(author, target)
            except IntegrityError:
                return Response(status=status.HTTP_409_CONFLICT)
            else:
                return Response(status=status.HTTP_201_CREATED)
        elif action == "remove":
            is_deleted, __ = self.remove_bind(author, target)
            if is_deleted:
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            raise ValidationError(f"Action {action} is not allowed. Allowed actions: [add, remove]")


class WishlistView(BaseModelBinderView):
    @staticmethod
    def add_bind(author, target):
        return author.add_to_wishlist(target)

    @staticmethod
    def remove_bind(author, target):
        return author.remove_from_wishlist(target)


class BlacklistView(BaseModelBinderView):
    @staticmethod
    def add_bind(author, target):
        return author.add_to_blacklist(target)

    @staticmethod
    def remove_bind(author, target):
        return author.remove_from_blacklist(target)


__all__ = ['WishlistView', 'BlacklistView']
