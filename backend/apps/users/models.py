from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model for the Community Feed.
    Karma is NOT stored here - it's calculated dynamically from KarmaTransaction.
    """
    avatar_url = models.URLField(max_length=500, blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']

    def __str__(self):
        return self.username


class KarmaTransaction(models.Model):
    """
    Records every karma-earning event.
    This is the source of truth for karma calculations.
    The leaderboard queries this table to calculate karma in the last 24 hours.
    """
    KARMA_TYPE_POST_LIKE = 'post_like'
    KARMA_TYPE_COMMENT_LIKE = 'comment_like'

    KARMA_TYPE_CHOICES = [
        (KARMA_TYPE_POST_LIKE, 'Post Like'),
        (KARMA_TYPE_COMMENT_LIKE, 'Comment Like'),
    ]

    # Points awarded for each type
    KARMA_POINTS = {
        KARMA_TYPE_POST_LIKE: 5,
        KARMA_TYPE_COMMENT_LIKE: 1,
    }

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='karma_transactions'
    )
    karma_type = models.CharField(max_length=20, choices=KARMA_TYPE_CHOICES)
    points = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    # Store reference to what earned the karma (for audit purposes)
    content_type = models.CharField(max_length=20)  # 'post' or 'comment'
    object_id = models.PositiveIntegerField()

    class Meta:
        db_table = 'karma_transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user.username}: +{self.points} ({self.karma_type})"
