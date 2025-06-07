from typing import ClassVar

from rest_framework import status, viewsets
from rest_framework.response import Response

from api.permissions import IsOwnerOrReadOnly

from .models import Profile
from .serializers import ProfileSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for the Profile model"""

    queryset = Profile.objects.select_related('owner').all()
    serializer_class = ProfileSerializer
    permission_classes: ClassVar[list] = [IsOwnerOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        """Allow users to delete their own profile"""
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
