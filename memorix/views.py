from typing import ClassVar

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from api.permissions import IsOwnerOrReadOnly
from common.actions import LeaderboardActionMixin, ScoreActionMixin
from common.filters import LeaderboardFilter, ScoreFilter
from common.viewset import GameLeaderboardViewSetMixin, GameScoreViewSetMixin

from .models import Category, Leaderboard
from .serializers import (
    CategorySerializer,
    LeaderboardSerializer,
    ScoreSerializer,
)


class BaseGameViewSetMixin:
    """Mixin providing common game-related functionality for ViewSets."""

    def get_category_or_404(self, category_code):
        """Get category by code or return 404 response."""
        from .models import Category

        try:
            return Category.objects.get(code=category_code.upper())
        except Category.DoesNotExist:
            return None

    def require_authentication(self, request):
        """Check if user is authenticated, return error response if not."""
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Authentication required.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return None

    def get_user_profile_or_404(self, request):
        """Get user's profile or return 404 response."""
        if not request.user.is_authenticated:
            return None
        return getattr(request.user, 'profile', None)


class ScorePagination(PageNumberPagination):
    """Pagination class for scores"""

    page_size = 3


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for game categories"""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes: ClassVar[list] = [permissions.AllowAny]
    filter_backends: ClassVar[list] = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]
    filterset_fields: ClassVar[list[str]] = ['code', 'name']
    search_fields: ClassVar[list[str]] = ['name', 'code', 'description']
    ordering_fields: ClassVar[list[str]] = ['name', 'code', 'created_at']
    ordering: ClassVar[list[str]] = ['name']


class ScoreViewSet(
    BaseGameViewSetMixin,
    ScoreActionMixin,
    GameScoreViewSetMixin,
    viewsets.ModelViewSet,
):
    """ViewSet for managing game scores."""

    serializer_class = ScoreSerializer
    permission_classes: ClassVar[list] = [IsOwnerOrReadOnly]
    pagination_class = ScorePagination
    filter_backends: ClassVar[list] = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]
    filterset_class = ScoreFilter
    search_fields: ClassVar[list[str]] = [
        'category__name',
        'profile__owner__username',
    ]
    ordering_fields: ClassVar[list[str]] = [
        'completed_at',
        'moves',
        'time_seconds',
        'stars',
    ]
    ordering: ClassVar[list[str]] = ['-completed_at']

    @action(detail=False, methods=['get'])
    def best(self, request):
        """Get user's best scores across all categories."""
        return self.handle_best_scores(request)

    @action(detail=False, methods=['get'], url_path='recent')
    def recent_scores(self, request):
        """Get user's most recent game scores."""
        return self.handle_recent_scores(request)

    @action(
        detail=False,
        methods=['get'],
        url_path='category/(?P<category_code>[^/.]+)',
    )
    def by_category(self, request, category_code=None):
        """Get user's scores for a specific category."""
        return self.handle_scores_by_category(request, category_code)

    @action(
        detail=False,
        methods=['delete'],
        url_path='clear/(?P<category_code>[^/.]+)',
    )
    def clear_category_scores(self, request, category_code=None):
        """Clear all user's scores for a specific category."""
        return self.handle_clear_category_scores(request, category_code)

    @action(detail=False, methods=['delete'], url_path='clear-all')
    def clear_all_scores(self, request):
        """Clear all user's scores across all categories."""
        return self.handle_clear_all_scores(request)


class LeaderboardViewSet(
    LeaderboardActionMixin,
    GameLeaderboardViewSetMixin,
    viewsets.ReadOnlyModelViewSet,
):
    """ViewSet for managing game leaderboards."""

    queryset = Leaderboard.objects.all()
    serializer_class = LeaderboardSerializer
    permission_classes: ClassVar[list] = [permissions.AllowAny]
    filter_backends: ClassVar[list] = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]
    filterset_class = LeaderboardFilter
    search_fields: ClassVar[list[str]] = [
        'category__name',
        'category__code',
        'score__profile__owner__username',
    ]
    ordering_fields: ClassVar[list[str]] = [
        'rank',
        'category__code',
        'score__moves',
        'score__time_seconds',
    ]
    ordering: ClassVar[list[str]] = ['category', 'rank']

    @action(detail=False, methods=['get'], url_path='top/(?P<limit>[0-9]+)')
    def top_players(self, request, limit=None):
        """Get top N players across all categories."""
        return self.handle_top_players(request, limit)

    @action(detail=False, methods=['get'])
    def user_rank(self, request):
        """Get user's rankings across all categories."""
        return self.handle_user_rank(request)

    @action(
        detail=False,
        methods=['get'],
        url_path='category/(?P<category_code>[^/.]+)/top/(?P<limit>[0-9]+)',
    )
    def category_top(self, request, category_code=None, limit=None):
        """Get top players for a specific category."""
        return self.handle_category_top(request, category_code, limit)
