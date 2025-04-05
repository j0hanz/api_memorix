from rest_framework import viewsets

from api.permissions import IsOwnerOrReadOnly

from .models import Profile
from .serializers import ProfileSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for the Profile model"""

    queryset = Profile.objects.select_related('owner').all()
    serializer_class = ProfileSerializer
    permission_classes = [IsOwnerOrReadOnly]
