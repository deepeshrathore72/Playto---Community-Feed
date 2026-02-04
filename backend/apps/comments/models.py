from django.db import models
from django.conf import settings


class Comment(models.Model):
    """
    A comment on a post, supporting nested replies (threaded comments).
    
    Uses adjacency list model for storing the tree structure.
    parent = NULL means it's a top-level comment on the post.
    parent = another_comment_id means it's a reply to that comment.
    
    We also store the root post for ALL comments (including nested ones)
    to enable efficient bulk fetching of entire comment trees.
    """
    post = models.ForeignKey(
        'posts.Post',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='replies',
        null=True,
        blank=True
    )
    content = models.TextField(max_length=2000)
    like_count = models.PositiveIntegerField(default=0, db_index=True)
    
    # Depth in the tree (0 = top-level, 1 = reply to top-level, etc.)
    # This helps with efficient ordering and display
    depth = models.PositiveSmallIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'comments'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post', 'created_at']),
            models.Index(fields=['parent']),
        ]

    def __str__(self):
        return f"Comment by {self.author.username} on Post {self.post_id}"

    def save(self, *args, **kwargs):
        """Automatically set the depth based on parent."""
        if self.parent:
            self.depth = self.parent.depth + 1
        else:
            self.depth = 0
        super().save(*args, **kwargs)
