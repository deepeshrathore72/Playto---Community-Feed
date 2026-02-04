from rest_framework import serializers
from .models import Comment
from apps.users.serializers import UserMinimalSerializer


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for Comment model.
    Replies are handled in the view layer for efficiency.
    """
    author = UserMinimalSerializer(read_only=True)
    is_liked_by_user = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    reply_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id', 'post', 'author', 'parent', 'content',
            'like_count', 'depth', 'is_liked_by_user',
            'replies', 'reply_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'like_count', 'depth', 'created_at', 'updated_at']

    def get_is_liked_by_user(self, obj):
        """Check if the current user has liked this comment."""
        request = self.context.get('request')
        user_id = None
        
        if request:
            user_id = request.session.get('user_id')
        
        if not user_id:
            return False
        
        # Use prefetched likes if available
        if hasattr(obj, 'prefetched_likes'):
            return any(like.user_id == user_id for like in obj.prefetched_likes)
        
        return obj.comment_likes.filter(user_id=user_id).exists()

    def get_replies(self, obj):
        """
        Get nested replies. This uses data that's already been
        fetched and organized in the view to avoid N+1 queries.
        """
        # Check if we have pre-built reply data
        if hasattr(obj, '_replies_data'):
            return obj._replies_data
        return []

    def get_reply_count(self, obj):
        """Get the count of direct replies."""
        if hasattr(obj, '_reply_count'):
            return obj._reply_count
        return 0


class CommentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating comments."""
    
    class Meta:
        model = Comment
        fields = ['id', 'post', 'parent', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_parent(self, value):
        """Ensure parent comment belongs to the same post."""
        if value:
            post_id = self.initial_data.get('post')
            if value.post_id != int(post_id):
                raise serializers.ValidationError(
                    "Parent comment must belong to the same post."
                )
        return value
