from django.db.models import Prefetch
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Comment
from .serializers import CommentSerializer, CommentCreateSerializer
from .utils import build_comment_tree
from apps.likes.models import CommentLike
from apps.users.models import User
from apps.posts.models import Post


class PostCommentsView(APIView):
    """
    Get all comments for a post as a nested tree.
    
    This view solves the N+1 problem by:
    1. Fetching ALL comments for the post in ONE query
    2. Using select_related to join author data
    3. Using prefetch_related to batch-fetch likes
    4. Building the tree structure in Python (O(n))
    
    Result: Exactly 2-3 queries regardless of comment count or nesting depth.
    """

    def get(self, request, post_id):
        # Verify post exists
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response(
                {'error': 'Post not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        user_id = request.session.get('user_id')
        
        # Fetch ALL comments for this post in ONE query
        # select_related('author') joins the user table (one query)
        queryset = Comment.objects.filter(post=post).select_related('author')
        
        if user_id:
            # Prefetch the current user's likes for all these comments
            # This is ONE additional query, not N queries
            queryset = queryset.prefetch_related(
                Prefetch(
                    'comment_likes',
                    queryset=CommentLike.objects.filter(user_id=user_id),
                    to_attr='prefetched_likes'
                )
            )
        
        # Fetch all comments
        comments = list(queryset)
        
        # Build nested tree structure in Python (O(n) time complexity)
        comment_tree = build_comment_tree(
            comments,
            CommentSerializer,
            {'request': request}
        )
        
        return Response({
            'post_id': post_id,
            'count': len(comments),
            'comments': comment_tree
        })


class CommentCreateView(generics.CreateAPIView):
    """Create a new comment on a post."""
    serializer_class = CommentCreateSerializer

    def create(self, request, *args, **kwargs):
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
        comment = serializer.save(author=user)
        
        # Return the created comment with full data
        response_serializer = CommentSerializer(comment, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class CommentDetailView(generics.RetrieveDestroyAPIView):
    """Retrieve or delete a comment."""
    serializer_class = CommentSerializer

    def get_queryset(self):
        user_id = self.request.session.get('user_id')
        
        queryset = Comment.objects.select_related('author')
        
        if user_id:
            queryset = queryset.prefetch_related(
                Prefetch(
                    'comment_likes',
                    queryset=CommentLike.objects.filter(user_id=user_id),
                    to_attr='prefetched_likes'
                )
            )
        
        return queryset

    def destroy(self, request, *args, **kwargs):
        """Only allow the author to delete their comment."""
        user_id = request.session.get('user_id')
        if not user_id:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        comment = self.get_object()
        if comment.author_id != user_id:
            return Response(
                {'error': 'You can only delete your own comments'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().destroy(request, *args, **kwargs)
