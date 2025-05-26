from typing import ClassVar

from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from api.permissions import IsOwnerOrReadOnly
from common.leaderboard import get_category_leaderboard
from common.utils import get_best_scores_data, get_user_scores_queryset

from .models import Category
from .serializers import (
    CategorySerializer,
    LeaderboardSerializer,
    ScoreSerializer,
)


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

    def get_queryset(self):
        return get_user_scores_queryset(self.request)

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
        category_id = self.request.query_params.get('category')
        return get_category_leaderboard(category_id)
