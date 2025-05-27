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
        """Prevent profile deletion via API"""
        return Response(
            {'detail': 'Profile deletion is not allowed.'},
            status=status.HTTP_403_FORBIDDEN,
        )
