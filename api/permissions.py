from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Allows access only to owners for edit operations."""

    def has_permission(self, request, view):
        """Check if user has permission to access the view"""
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if hasattr(obj, 'profile') and hasattr(obj.profile, 'owner'):
            return obj.profile.owner == request.user
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False
