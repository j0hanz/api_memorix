from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle


class ScoreSubmissionThrottle(UserRateThrottle):
    """Security: Custom throttle for score submissions"""

    scope = 'score_submit'


class GamePermissionMixin:
    """Mixin for handling dynamic permissions based on actions."""

    def get_permissions(self):
        """Assign permissions based on action"""
        if self.action in ['leaderboard', 'best']:
            return [permissions.AllowAny()]
        return super().get_permissions()


class ScoreThrottleMixin:
    """Mixin for handling score-specific throttling."""

    def get_throttles(self):
        """Security: Apply stricter throttling to score creation"""
        if self.action == 'create':
            return [ScoreSubmissionThrottle()]
        return super().get_throttles()


class UserProfileQuerysetMixin:
    """Mixin for filtering queryset by authenticated user's profile."""

    def get_queryset(self):
        """Return queryset for the current user."""
        user = self.request.user
        if not user.is_authenticated:
            return self.model.objects.none()

        profile = getattr(user, 'profile', None)
        if not profile:
            return self.model.objects.none()

        return self.model.objects.filter(profile=profile).select_related(
            'profile', 'profile__owner', 'category'
        )

    @property
    def model(self):
        """Get the model class from the ViewSet's queryset or serializer."""
        if hasattr(self, 'queryset') and self.queryset is not None:
            return self.queryset.model
        elif hasattr(self, 'serializer_class'):
            return self.serializer_class.Meta.model
        else:
            raise AttributeError(
                'ViewSet must define queryset or serializer_class'
            )


class ScoreCRUDMixin:
    """Mixin for handling score-specific CRUD operations."""

    def update(self, request, *args, **kwargs):
        """Disable score updates"""
        return Response(
            {'detail': 'Method not allowed.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def partial_update(self, request, *args, **kwargs):
        """Disable partial score updates"""
        return Response(
            {'detail': 'Method not allowed.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def perform_create(self, serializer):
        """Save the score with the associated profile"""
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        """Delete a user's score with proper security checks."""
        score = self.get_object()
        if score.profile.owner != request.user:
            return Response(
                {'detail': 'You can only delete your own scores.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        category = score.category
        score.delete()

        from common.leaderboard import update_category_leaderboard

        update_category_leaderboard(category)

        return Response(
            {'detail': 'Score deleted successfully.'},
            status=status.HTTP_204_NO_CONTENT,
        )


class ReadOnlyUpdateMixin:
    """Mixin for disabling update operations on ViewSets."""

    def update(self, request, *args, **kwargs):
        """Disable updates"""
        return Response(
            {'detail': 'Method not allowed.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def partial_update(self, request, *args, **kwargs):
        """Disable partial updates"""
        return Response(
            {'detail': 'Method not allowed.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


class SecureDeleteMixin:
    """Mixin for secure delete operations with ownership validation."""

    def destroy(self, request, *args, **kwargs):
        """Delete with ownership validation."""
        obj = self.get_object()

        if hasattr(obj, 'profile') and obj.profile.owner != request.user:
            return Response(
                {'detail': 'You can only delete your own records.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        elif hasattr(obj, 'owner') and obj.owner != request.user:
            return Response(
                {'detail': 'You can only delete your own records.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        obj.delete()
        return Response(
            {'detail': 'Record deleted successfully.'},
            status=status.HTTP_204_NO_CONTENT,
        )


class OptimizedQuerysetMixin:
    """Mixin for optimizing querysets based on ViewSet actions."""

    def get_queryset(self):
        """Optimize queryset based on action."""
        queryset = super().get_queryset()

        if self.action == 'retrieve':
            return self.get_retrieve_queryset(queryset)
        elif self.action == 'list':
            return self.get_list_queryset(queryset)

        return queryset

    def get_retrieve_queryset(self, queryset):
        """Override this method to customize retrieve queryset optimization."""
        return queryset.select_related()

    def get_list_queryset(self, queryset):
        """Override this method to customize list queryset optimization."""
        return queryset.select_related()


class GameScoreViewSetMixin(
    GamePermissionMixin,
    ScoreThrottleMixin,
    UserProfileQuerysetMixin,
    ScoreCRUDMixin,
):
    """Mixin for game score ViewSets."""


class GameLeaderboardViewSetMixin(OptimizedQuerysetMixin):
    """Mixin for handling leaderboard ViewSets."""

    def get_retrieve_queryset(self, queryset):
        """Optimize queryset for single leaderboard entry retrieval."""
        return queryset.select_related(
            'score', 'score__profile', 'score__profile__owner', 'category'
        )

    def get_list_queryset(self, queryset):
        """Optimize queryset for leaderboard list."""
        return queryset.select_related(
            'score', 'score__profile', 'score__profile__owner', 'category'
        ).order_by('category', 'rank')


def validate_user_ownership(obj, user):
    """Validate that the user owns the given object."""
    if hasattr(obj, 'profile'):
        return obj.profile.owner == user
    elif hasattr(obj, 'owner'):
        return obj.owner == user
    return False


def get_user_profile_queryset(model, user):
    """Get queryset filtered by user's profile."""
    if not user.is_authenticated:
        return model.objects.none()

    profile = getattr(user, 'profile', None)
    if not profile:
        return model.objects.none()

    return model.objects.filter(profile=profile).select_related(
        'profile', 'profile__owner', 'category'
    )


def create_method_not_allowed_response(detail='Method not allowed.'):
    """Create a standardized method not allowed response."""
    return Response(
        {'detail': detail},
        status=status.HTTP_405_METHOD_NOT_ALLOWED,
    )


def create_forbidden_response(
    detail='You do not have permission to perform this action.',
):
    """Create a standardized forbidden response."""
    return Response(
        {'detail': detail},
        status=status.HTTP_403_FORBIDDEN,
    )


def create_success_response(
    detail='Operation completed successfully.', status_code=status.HTTP_200_OK
):
    """Create a standardized success response."""
    return Response(
        {'detail': detail},
        status=status_code,
    )
