from typing import ClassVar

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle

from api.permissions import IsOwnerOrReadOnly
from common.leaderboard import get_category_leaderboard
from common.utils import get_best_scores_data, get_user_scores_queryset

from .models import Category, Leaderboard
from .serializers import (
    CategorySerializer,
    LeaderboardSerializer,
    ScoreSerializer,
)


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


class ScoreViewSet(viewsets.ModelViewSet):
    """ViewSet for game results"""

    serializer_class = ScoreSerializer
    permission_classes: ClassVar[list] = [IsOwnerOrReadOnly]
    pagination_class = ScorePagination

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
        return get_user_scores_queryset(self.request)

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
        data = get_best_scores_data(request, self.get_serializer_class())
        return Response(data)


class LeaderboardViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for leaderboard"""

    serializer_class = LeaderboardSerializer
    permission_classes: ClassVar[list] = [permissions.AllowAny]

    def get_queryset(self):
        if self.action == 'retrieve':
            return Leaderboard.objects.select_related(
                'score', 'score__profile', 'score__profile__owner', 'category'
            )
        category_id = self.request.query_params.get('category')
        leaderboard_entries = get_category_leaderboard(category_id)
        if leaderboard_entries:
            entry_ids = [entry.id for entry in leaderboard_entries]
            return Leaderboard.objects.filter(id__in=entry_ids).order_by(
                'category', 'rank'
            )
        else:
            return Leaderboard.objects.none()
