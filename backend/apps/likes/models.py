from django.db import models
from django.conf import settings


class PostLike(models.Model):
    """
    A like on a post.
    
    The unique_together constraint prevents double-likes at the database level.
    This is crucial for preventing race conditions - even if two requests
    arrive simultaneously, only one can create the like record.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='post_likes'
    )
    post = models.ForeignKey(
        'posts.Post',
        on_delete=models.CASCADE,
        related_name='post_likes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'post_likes'
        # This unique constraint prevents double-likes at DB level
        unique_together = ['user', 'post']
        indexes = [
            models.Index(fields=['post', 'user']),
        ]

    def __str__(self):
        return f"{self.user.username} likes Post {self.post_id}"


class CommentLike(models.Model):
    """
    A like on a comment.
    
    Same unique constraint pattern as PostLike for race condition prevention.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comment_likes'
    )
    comment = models.ForeignKey(
        'comments.Comment',
        on_delete=models.CASCADE,
        related_name='comment_likes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'comment_likes'
        # This unique constraint prevents double-likes at DB level
        unique_together = ['user', 'comment']
        indexes = [
            models.Index(fields=['comment', 'user']),
        ]

    def __str__(self):
        return f"{self.user.username} likes Comment {self.comment_id}"
