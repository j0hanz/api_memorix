from typing import ClassVar

from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.permissions import IsOwnerOrReadOnly
from common.score_utils import get_leaderboard_scores, get_user_best_scores

from .models import Category, Score
from .serializers import CategorySerializer, ScoreSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for game categories"""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes: ClassVar[list] = [IsOwnerOrReadOnly]


class ScoreViewSet(viewsets.ModelViewSet):
    """ViewSet for game results"""

    serializer_class = ScoreSerializer
    permission_classes: ClassVar[list] = [IsOwnerOrReadOnly]

    def get_permissions(self):
        if self.action == 'leaderboard':
            return [permissions.AllowAny()]
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        """Return results filtered by user"""
        user = self.request.user
        if not user.is_authenticated:
            return Score.objects.none()
        if user.is_staff:
            return Score.objects.all()
        profile = getattr(user, 'profile', None)
        if profile is not None:
            return Score.objects.filter(profile=profile)
        return Score.objects.none()

    def perform_create(self, serializer):
        """Pass the request context to the serializer"""
        serializer.save()

    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        """Get the leaderboard for a specific category"""
        category_id = request.query_params.get('category')
        top_results = get_leaderboard_scores(category_id)
        serializer = self.get_serializer(top_results, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def best(self, request):
        """Get the user's best scores for each category"""
        user = self.request.user
        if not user.is_authenticated:
            return Response([])
        profile = getattr(user, 'profile', None)
        if not profile:
            return Response([])
        best_scores = get_user_best_scores(profile)
        serializer = self.get_serializer(best_scores, many=True)
        return Response(serializer.data)
