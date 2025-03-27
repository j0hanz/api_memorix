from rest_framework.exceptions import APIException
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class RootRoute(APIView):
    """Root API endpoint."""

    def get(self, request: Request) -> Response:
        try:
            return Response({'message': 'Memorix API is running!'})
        except Exception as e:
            msg = f'An error occurred: {str(e)}'
            raise APIException(msg)
