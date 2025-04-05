from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class RootRoute(APIView):
    """Root API endpoint."""

    permission_classes = [permissions.AllowAny]

    def get(self, request: Request) -> Response:
        return Response({'message': 'Memorix API is running!'})
