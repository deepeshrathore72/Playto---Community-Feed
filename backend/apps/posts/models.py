from django.db import models
from django.conf import settings


class Post(models.Model):
    """
    A text post in the community feed.
    Like count is denormalized for performance but should be kept in sync.
    """
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    content = models.TextField(max_length=5000)
    like_count = models.PositiveIntegerField(default=0, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'posts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at', 'id']),
        ]

    def __str__(self):
        return f"Post by {self.author.username}: {self.content[:50]}..."
