from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.users.models import User
from . import services


class PostLikeToggleView(APIView):
    """
    Toggle like on a post.
    
    POST /api/likes/post/<post_id>/toggle/
    
    This endpoint handles both liking and unliking a post.
    Race conditions are handled in the service layer using:
    - Database unique constraints
    - Atomic transactions
    - F() expressions for count updates
    """

    def post(self, request, post_id):
        user_id = request.session.get('user_id')
        if not user_id:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        success, message, like_count = services.toggle_post_like(user, post_id)
        
        if like_count is None:
            return Response(
                {'error': message},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response({
            'success': success,
            'message': message,
            'like_count': like_count,
            'is_liked': success and 'liked' in message.lower() and 'unliked' not in message.lower()
        })


class CommentLikeToggleView(APIView):
    """
    Toggle like on a comment.
    
    POST /api/likes/comment/<comment_id>/toggle/
    """

    def post(self, request, comment_id):
        user_id = request.session.get('user_id')
        if not user_id:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        success, message, like_count = services.toggle_comment_like(user, comment_id)
        
        if like_count is None:
            return Response(
                {'error': message},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response({
            'success': success,
            'message': message,
            'like_count': like_count,
            'is_liked': success and 'liked' in message.lower() and 'unliked' not in message.lower()
        })
