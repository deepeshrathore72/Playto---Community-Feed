from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User
from .serializers import UserSerializer, UserCreateSerializer


class UserListCreateView(generics.ListCreateAPIView):
    """List all users or create a new user."""
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer


class UserDetailView(generics.RetrieveAPIView):
    """Retrieve a specific user."""
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CurrentUserView(APIView):
    """
    Get or set the current user for the session.
    This is a simplified auth mechanism for the demo.
    """

    def get(self, request):
        user_id = request.session.get('user_id')
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                serializer = UserSerializer(user)
                return Response(serializer.data)
            except User.DoesNotExist:
                pass
        return Response({'user': None}, status=status.HTTP_200_OK)

    def post(self, request):
        """Login: Set the current user by username."""
        username = request.data.get('username')
        if not username:
            return Response(
                {'error': 'Username is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(username=username)
            request.session['user_id'] = user.id
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request):
        """Logout: Clear the current user."""
        request.session.pop('user_id', None)
        return Response(status=status.HTTP_204_NO_CONTENT)
