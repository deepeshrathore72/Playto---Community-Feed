"""
Health check views for debugging deployment issues.
"""
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import connection
from apps.users.models import User
from apps.posts.models import Post
from apps.comments.models import Comment
from apps.likes.models import PostLike, CommentLike


class HealthCheckView(APIView):
    """
    Health check endpoint that shows database statistics.
    Useful for verifying deployment and database connectivity.
    
    GET /api/health/
    """
    
    def get(self, request):
        # Get database info
        db_vendor = connection.vendor
        db_name = connection.settings_dict.get('NAME', 'unknown')
        
        # Get counts
        user_count = User.objects.count()
        post_count = Post.objects.count()
        comment_count = Comment.objects.count()
        post_like_count = PostLike.objects.count()
        comment_like_count = CommentLike.objects.count()
        
        # Get sample users
        users = list(User.objects.values('id', 'username')[:10])
        
        return Response({
            'status': 'healthy',
            'database': {
                'vendor': db_vendor,
                'name': db_name,
            },
            'stats': {
                'users': user_count,
                'posts': post_count,
                'comments': comment_count,
                'post_likes': post_like_count,
                'comment_likes': comment_like_count,
            },
            'sample_users': users,
        })
