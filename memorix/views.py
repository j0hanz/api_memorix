from typing import ClassVar

from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from api.permissions import IsOwnerOrReadOnly
from common.score_utils import get_leaderboard_scores, get_user_best_scores

from .models import Category, Score
from .serializers import CategorySerializer, ScoreSerializer


class ScorePagination(PageNumberPagination):
    """Pagination class for scores"""

    page_size = 5


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for game categories"""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes: ClassVar[list] = [IsOwnerOrReadOnly]


class ScoreViewSet(viewsets.ModelViewSet):
    """ViewSet for game results"""

    serializer_class = ScoreSerializer
    permission_classes: ClassVar[list] = [IsOwnerOrReadOnly]
    pagination_class = ScorePagination

    def get_permissions(self):
        """Assign permissions based on action"""
        if self.action in ['leaderboard']:
            return [permissions.AllowAny()]
        return super().get_permissions()

    def get_queryset(self):
        """Retrieve scores for the authenticated user"""
        user = self.request.user
        if not user.is_authenticated:
            return Score.objects.none()
        profile = getattr(user, 'profile', None)
        queryset = (
            Score.objects.filter(profile=profile)
            if profile
            else Score.objects.none()
        )
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__code=category.upper())
        return queryset

    def perform_create(self, serializer):
        """Save the score with the associated profile"""
        serializer.save()

    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        """Retrieve leaderboard scores for a specific category"""
        category_id = request.query_params.get('category')
        top_results = get_leaderboard_scores(category_id)
        serializer = self.get_serializer(top_results, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def best(self, request):
        """Retrieve the best scores for the authenticated user"""
        user = request.user
        profile = getattr(user, 'profile', None)
        if not user.is_authenticated or not profile:
            return Response([])
        best_scores = get_user_best_scores(profile)
        serializer = self.get_serializer(best_scores, many=True)
        return Response(serializer.data)
