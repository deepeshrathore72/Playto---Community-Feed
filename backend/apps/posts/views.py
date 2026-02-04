from django.db.models import Count, Prefetch
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Post
from .serializers import PostSerializer, PostCreateSerializer
from apps.likes.models import PostLike
from apps.users.models import User


class PostListCreateView(generics.ListCreateAPIView):
    """
    List all posts or create a new post.
    
    GET: Returns paginated list of posts with author info and like counts.
    Uses select_related and prefetch_related to avoid N+1 queries.
    
    POST: Creates a new post for the current user.
    """

    def get_queryset(self):
        """
        Optimized queryset that:
        1. Joins author data (select_related) - single JOIN
        2. Prefetches likes for current user (prefetch_related) - single query
        3. Annotates comment count - single query with aggregation
        
        This results in exactly 2-3 queries regardless of the number of posts.
        """
        user_id = self.request.session.get('user_id')
        
        queryset = Post.objects.select_related('author').annotate(
            comment_count_annotated=Count('comments')
        )
        
        if user_id:
            # Prefetch only the current user's likes for the "is_liked" check
            queryset = queryset.prefetch_related(
                Prefetch(
                    'post_likes',
                    queryset=PostLike.objects.filter(user_id=user_id),
                    to_attr='prefetched_likes'
                )
            )
        
        return queryset.order_by('-created_at')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PostCreateSerializer
        return PostSerializer

    def create(self, request, *args, **kwargs):
        """Create a post for the current user."""
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
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        post = serializer.save(author=user)
        
        # Return full post data
        response_serializer = PostSerializer(post, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class PostDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single post with all its details.
    """
    serializer_class = PostSerializer

    def get_queryset(self):
        user_id = self.request.session.get('user_id')
        
        queryset = Post.objects.select_related('author').annotate(
            comment_count_annotated=Count('comments')
        )
        
        if user_id:
            queryset = queryset.prefetch_related(
                Prefetch(
                    'post_likes',
                    queryset=PostLike.objects.filter(user_id=user_id),
                    to_attr='prefetched_likes'
                )
            )
        
        return queryset
