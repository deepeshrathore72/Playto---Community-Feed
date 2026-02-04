"""
Like service module that handles the business logic for likes.

This module provides atomic operations for liking/unliking posts and comments,
with proper handling of:
1. Race conditions (using database transactions and unique constraints)
2. Karma tracking (creating KarmaTransaction records)
3. Like count denormalization (updating counts on Post/Comment models)
"""
from django.db import transaction, IntegrityError
from django.db.models import F
from .models import PostLike, CommentLike
from apps.posts.models import Post
from apps.comments.models import Comment
from apps.users.models import KarmaTransaction


def like_post(user, post_id):
    """
    Like a post with proper concurrency handling.
    
    Strategy for preventing double-likes and race conditions:
    1. Database UNIQUE constraint on (user, post) prevents duplicates
    2. Atomic transaction ensures all-or-nothing execution
    3. F() expressions for incrementing counts prevent race conditions
    
    Returns:
        tuple: (success: bool, message: str, new_like_count: int or None)
    """
    try:
        with transaction.atomic():
            # Get the post (with row-level lock for the update)
            post = Post.objects.select_for_update().get(id=post_id)
            
            # Try to create the like - unique constraint prevents duplicates
            # If user already liked, IntegrityError is raised
            PostLike.objects.create(user=user, post=post)
            
            # Increment like count using F() to prevent race conditions
            # F() generates SQL: UPDATE posts SET like_count = like_count + 1
            # This is atomic at the database level
            Post.objects.filter(id=post_id).update(like_count=F('like_count') + 1)
            
            # Create karma transaction for the post author
            if post.author_id != user.id:  # Don't give karma for self-likes
                KarmaTransaction.objects.create(
                    user=post.author,
                    karma_type=KarmaTransaction.KARMA_TYPE_POST_LIKE,
                    points=KarmaTransaction.KARMA_POINTS[KarmaTransaction.KARMA_TYPE_POST_LIKE],
                    content_type='post',
                    object_id=post_id
                )
            
            # Refresh to get updated count
            post.refresh_from_db()
            return True, 'Post liked successfully', post.like_count
            
    except Post.DoesNotExist:
        return False, 'Post not found', None
    except IntegrityError:
        # User already liked this post - unique constraint violation
        post = Post.objects.get(id=post_id)
        return False, 'You have already liked this post', post.like_count


def unlike_post(user, post_id):
    """
    Unlike a post with proper concurrency handling.
    
    Returns:
        tuple: (success: bool, message: str, new_like_count: int or None)
    """
    try:
        with transaction.atomic():
            post = Post.objects.select_for_update().get(id=post_id)
            
            # Try to find and delete the like
            deleted_count, _ = PostLike.objects.filter(
                user=user, post=post
            ).delete()
            
            if deleted_count == 0:
                return False, 'You have not liked this post', post.like_count
            
            # Decrement like count using F() expression
            Post.objects.filter(id=post_id).update(
                like_count=F('like_count') - 1
            )
            
            # Remove the karma transaction
            if post.author_id != user.id:
                KarmaTransaction.objects.filter(
                    user=post.author,
                    karma_type=KarmaTransaction.KARMA_TYPE_POST_LIKE,
                    content_type='post',
                    object_id=post_id
                ).delete()
            
            post.refresh_from_db()
            return True, 'Post unliked successfully', post.like_count
            
    except Post.DoesNotExist:
        return False, 'Post not found', None


def like_comment(user, comment_id):
    """
    Like a comment with proper concurrency handling.
    
    Same strategy as like_post for race condition prevention.
    """
    try:
        with transaction.atomic():
            comment = Comment.objects.select_for_update().get(id=comment_id)
            
            CommentLike.objects.create(user=user, comment=comment)
            
            Comment.objects.filter(id=comment_id).update(
                like_count=F('like_count') + 1
            )
            
            # Create karma transaction for the comment author
            if comment.author_id != user.id:
                KarmaTransaction.objects.create(
                    user=comment.author,
                    karma_type=KarmaTransaction.KARMA_TYPE_COMMENT_LIKE,
                    points=KarmaTransaction.KARMA_POINTS[KarmaTransaction.KARMA_TYPE_COMMENT_LIKE],
                    content_type='comment',
                    object_id=comment_id
                )
            
            comment.refresh_from_db()
            return True, 'Comment liked successfully', comment.like_count
            
    except Comment.DoesNotExist:
        return False, 'Comment not found', None
    except IntegrityError:
        comment = Comment.objects.get(id=comment_id)
        return False, 'You have already liked this comment', comment.like_count


def unlike_comment(user, comment_id):
    """
    Unlike a comment with proper concurrency handling.
    """
    try:
        with transaction.atomic():
            comment = Comment.objects.select_for_update().get(id=comment_id)
            
            deleted_count, _ = CommentLike.objects.filter(
                user=user, comment=comment
            ).delete()
            
            if deleted_count == 0:
                return False, 'You have not liked this comment', comment.like_count
            
            Comment.objects.filter(id=comment_id).update(
                like_count=F('like_count') - 1
            )
            
            if comment.author_id != user.id:
                KarmaTransaction.objects.filter(
                    user=comment.author,
                    karma_type=KarmaTransaction.KARMA_TYPE_COMMENT_LIKE,
                    content_type='comment',
                    object_id=comment_id
                ).delete()
            
            comment.refresh_from_db()
            return True, 'Comment unliked successfully', comment.like_count
            
    except Comment.DoesNotExist:
        return False, 'Comment not found', None


def toggle_post_like(user, post_id):
    """
    Toggle like status on a post.
    If liked, unlike. If not liked, like.
    """
    # Check if already liked
    exists = PostLike.objects.filter(user=user, post_id=post_id).exists()
    
    if exists:
        return unlike_post(user, post_id)
    else:
        return like_post(user, post_id)


def toggle_comment_like(user, comment_id):
    """
    Toggle like status on a comment.
    """
    exists = CommentLike.objects.filter(user=user, comment_id=comment_id).exists()
    
    if exists:
        return unlike_comment(user, comment_id)
    else:
        return like_comment(user, comment_id)
