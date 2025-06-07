from typing import ClassVar

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.permissions import IsOwnerOrReadOnly

from .models import Profile
from .serializers import ProfileSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user profiles."""

    queryset = Profile.objects.select_related('owner').all()
    serializer_class = ProfileSerializer
    permission_classes: ClassVar[list] = [IsOwnerOrReadOnly]
    filterset_fields: ClassVar[list[str]] = [
        'owner__username',
        'created_at',
        'updated_at',
    ]

    def get_permissions(self):
        """Determine permissions based on action."""
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return super().get_permissions()

    def get_queryset(self):
        """Optimize queryset based on action."""
        if self.action in ['retrieve', 'update', 'partial_update']:
            return self.queryset.select_related('owner')
        return self.queryset

    def destroy(self, request, *args, **kwargs):
        """Delete a user profile."""
        profile = self.get_object()

        if profile.owner != request.user:
            return Response(
                {'detail': 'You can only delete your own profile.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        profile.delete()

        return Response(
            {'detail': 'Profile deleted successfully.'},
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(
        detail=True, methods=['post'], permission_classes=[IsOwnerOrReadOnly]
    )
    def upload_image(self, request, pk=None):
        """Upload a profile picture."""
        profile = self.get_object()

        if 'profile_picture' not in request.data:
            return Response(
                {'detail': 'No image file provided.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(
            profile,
            data={'profile_picture': request.data['profile_picture']},
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get profile statistics."""
        profile = self.get_object()

        from django.db.models import Avg, Count, Max, Min

        from memorix.models import Score

        stats_data = Score.objects.filter(profile=profile).aggregate(
            total_games=Count('id'),
            avg_moves=Avg('moves'),
            avg_time=Avg('time_seconds'),
            avg_stars=Avg('stars'),
            best_moves=Min('moves'),
            fastest_time=Min('time_seconds'),
            max_stars=Max('stars'),
        )

        return Response(
            {
                'profile_id': profile.id,
                'username': profile.owner.username,
                'total_games_played': stats_data['total_games'] or 0,
                'average_moves': round(stats_data['avg_moves'], 2)
                if stats_data['avg_moves']
                else 0,
                'average_time': round(stats_data['avg_time'], 2)
                if stats_data['avg_time']
                else 0,
                'average_stars': round(stats_data['avg_stars'], 2)
                if stats_data['avg_stars']
                else 0,
                'best_moves': stats_data['best_moves'],
                'fastest_time': stats_data['fastest_time'],
                'max_stars': stats_data['max_stars'],
            }
        )

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get the authenticated user's profile."""
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Authentication required.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            profile = request.user.profile
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        except Profile.DoesNotExist:
            return Response(
                {'detail': 'Profile not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
