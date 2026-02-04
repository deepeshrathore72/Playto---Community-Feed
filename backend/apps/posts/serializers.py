from rest_framework import serializers
from .models import Post
from apps.users.serializers import UserMinimalSerializer


class PostSerializer(serializers.ModelSerializer):
    """
    Serializer for Post model.
    Includes nested author info and computed fields.
    """
    author = UserMinimalSerializer(read_only=True)
    is_liked_by_user = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'author', 'content', 'like_count',
            'is_liked_by_user', 'comment_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'like_count', 'created_at', 'updated_at']

    def get_is_liked_by_user(self, obj):
        """Check if the current user has liked this post."""
        request = self.context.get('request')
        user_id = None
        
        if request:
            user_id = request.session.get('user_id')
        
        if not user_id:
            return False
        
        # Use prefetched likes if available
        if hasattr(obj, 'prefetched_likes'):
            return any(like.user_id == user_id for like in obj.prefetched_likes)
        
        return obj.post_likes.filter(user_id=user_id).exists()

    def get_comment_count(self, obj):
        """Get the total number of comments on this post."""
        if hasattr(obj, 'comment_count_annotated'):
            return obj.comment_count_annotated
        return obj.comments.count()


class PostCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating posts."""
    
    class Meta:
        model = Post
        fields = ['id', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']
