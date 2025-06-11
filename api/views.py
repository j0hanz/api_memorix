from typing import ClassVar

from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LogoutSerializer


class RootRoute(APIView):
    """Root API endpoint."""

    permission_classes: ClassVar[list] = [permissions.AllowAny]

    def get(self, request: Request) -> Response:
        return Response({'message': 'Memorix API is running!'})


class LogoutView(APIView):
    """Custom logout view with JWT blacklisting"""

    permission_classes: ClassVar[list] = [permissions.IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request: Request) -> Response:
        """Logout user and blacklist refresh token"""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            return Response(
                {'detail': 'Logout successful.'}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
