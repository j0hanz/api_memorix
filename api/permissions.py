from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Allows access only to owners for edit operations."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user
