from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Permission to only allow owners to edit objects."""

    def has_object_permission(
        self, request: Request, view: APIView, obj: object
    ) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        owner = getattr(obj, 'owner', getattr(obj, 'user', None))
        return owner == request.user
