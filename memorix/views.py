from typing import ClassVar

from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.permissions import IsOwnerOrReadOnly

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
        queryset = Score.objects.all()
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        top_results = queryset.order_by('-stars', 'time_seconds', 'moves')[:10]
        serializer = self.get_serializer(top_results, many=True)
        return Response(serializer.data)
