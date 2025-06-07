from typing import ClassVar

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle

from api.permissions import IsOwnerOrReadOnly
from common.filters import LeaderboardFilter, ScoreFilter
from common.utils import get_best_scores_data

from .models import Category, Leaderboard, Score
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


class ScoreSubmissionThrottle(UserRateThrottle):
    """Security: Custom throttle for score submissions"""

    scope = 'score_submit'


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


class ScoreViewSet(BaseGameViewSetMixin, viewsets.ModelViewSet):
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

    def get_permissions(self):
        """Assign permissions based on action"""
        if self.action in ['leaderboard', 'best']:
            return [permissions.AllowAny()]
        return super().get_permissions()

    def get_throttles(self):
        """Security: Apply stricter throttling to score creation"""
        if self.action == 'create':
            return [ScoreSubmissionThrottle()]
        return super().get_throttles()

    def get_queryset(self):
        """Return queryset for the current user."""
        user = self.request.user
        if not user.is_authenticated:
            return Score.objects.none()

        profile = getattr(user, 'profile', None)
        if not profile:
            return Score.objects.none()

        return Score.objects.filter(profile=profile).select_related(
            'profile', 'profile__owner', 'category'
        )

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

    @action(detail=False, methods=['get'])
    def best(self, request):
        """Get user's best scores across all categories."""
        data = get_best_scores_data(request, self.get_serializer_class())
        return Response(data)

    @action(detail=False, methods=['get'], url_path='recent')
    def recent_scores(self, request):
        """Get user's most recent game scores."""
        queryset = self.get_queryset().order_by('-completed_at')[:10]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['get'],
        url_path='category/(?P<category_code>[^/.]+)',
    )
    def by_category(self, request, category_code=None):
        """Get user's scores for a specific category."""
        category = self.get_category_or_404(category_code)
        if not category:
            return Response(
                {'detail': 'Category not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        queryset = self.filter_queryset(
            self.get_queryset().filter(category=category)
        )
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class LeaderboardViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for managing game leaderboards."""

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

    def get_queryset(self):
        """Optimize queryset based on action."""
        if self.action == 'retrieve':
            return Leaderboard.objects.select_related(
                'score', 'score__profile', 'score__profile__owner', 'category'
            )
        return Leaderboard.objects.select_related(
            'score', 'score__profile', 'score__profile__owner', 'category'
        ).order_by('category', 'rank')

    @action(detail=False, methods=['get'], url_path='top/(?P<limit>[0-9]+)')
    def top_players(self, request, limit=None):
        """Get top N players across all categories."""
        try:
            limit = min(int(limit), 100)
        except (ValueError, TypeError):
            limit = 10

        queryset = self.get_queryset()[:limit]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def user_rank(self, request):
        """Get user's rankings across all categories."""
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Authentication required.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user_ranks = []
        user_profile = getattr(request.user, 'profile', None)

        if user_profile:
            from .models import Category

            for category in Category.objects.all():
                try:
                    leaderboard_entry = Leaderboard.objects.get(
                        score__profile=user_profile, category=category
                    )
                    user_ranks.append(
                        {
                            'category': category.name,
                            'category_code': category.code,
                            'rank': leaderboard_entry.rank,
                            'score_id': leaderboard_entry.score.id,
                        }
                    )
                except Leaderboard.DoesNotExist:
                    continue

        return Response(
            {'username': request.user.username, 'rankings': user_ranks}
        )

    @action(
        detail=False,
        methods=['get'],
        url_path='category/(?P<category_code>[^/.]+)/top/(?P<limit>[0-9]+)',
    )
    def category_top(self, request, category_code=None, limit=None):
        """Get top players for a specific category."""
        from .models import Category

        try:
            category = Category.objects.get(code=category_code.upper())
            limit = min(int(limit), 50)
        except (ValueError, TypeError):
            limit = 10
        except Category.DoesNotExist:
            return Response(
                {'detail': 'Category not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        queryset = (
            Leaderboard.objects.filter(category=category)
            .select_related('score', 'score__profile', 'score__profile__owner')
            .order_by('rank')[:limit]
        )

        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                'category': category.name,
                'category_code': category.code,
                'leaderboard': serializer.data,
            }
        )
