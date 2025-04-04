from rest_framework import generics

from api.permissions import IsOwnerOrReadOnly

from .models import Profile
from .serializers import ProfileSerializer


class ProfileListCreateView(generics.ListCreateAPIView):
    """View to list and create profiles."""

    queryset = Profile.objects.select_related('owner').all()
    serializer_class = ProfileSerializer


class ProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View to retrieve, update, or delete a profile."""

    permission_classes = [IsOwnerOrReadOnly]
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
