"""
Tests for the like functionality including concurrency handling.
"""
from django.test import TestCase
from django.db import IntegrityError
from apps.users.models import User, KarmaTransaction
from apps.posts.models import Post
from apps.comments.models import Comment
from apps.likes.models import PostLike, CommentLike
from apps.likes.services import like_post, unlike_post, toggle_post_like


class LikeServiceTests(TestCase):
    """Test the like service functions."""

    def setUp(self):
        """Create test users and posts."""
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@test.com',
            password='testpass123'
        )
        self.post = Post.objects.create(
            author=self.user1,
            content='Test post'
        )

    def test_like_post_success(self):
        """Test successful post like."""
        success, message, like_count = like_post(self.user2, self.post.id)
        
        self.assertTrue(success)
        self.assertEqual(like_count, 1)
        self.assertTrue(PostLike.objects.filter(user=self.user2, post=self.post).exists())

    def test_like_post_creates_karma(self):
        """Test that liking a post creates karma for the author."""
        like_post(self.user2, self.post.id)
        
        # Check karma transaction was created
        karma = KarmaTransaction.objects.filter(
            user=self.user1,
            karma_type=KarmaTransaction.KARMA_TYPE_POST_LIKE
        ).first()
        
        self.assertIsNotNone(karma)
        self.assertEqual(karma.points, 5)

    def test_double_like_prevented(self):
        """Test that double-likes are prevented."""
        # First like
        success1, _, _ = like_post(self.user2, self.post.id)
        self.assertTrue(success1)
        
        # Second like attempt
        success2, message, _ = like_post(self.user2, self.post.id)
        self.assertFalse(success2)
        self.assertIn('already liked', message.lower())
        
        # Should still only be 1 like
        self.assertEqual(PostLike.objects.filter(post=self.post).count(), 1)
        self.post.refresh_from_db()
        self.assertEqual(self.post.like_count, 1)

    def test_self_like_no_karma(self):
        """Test that self-likes don't create karma."""
        like_post(self.user1, self.post.id)  # Author likes own post
        
        # Should be no karma transaction
        karma_count = KarmaTransaction.objects.filter(
            user=self.user1,
            content_type='post',
            object_id=self.post.id
        ).count()
        
        self.assertEqual(karma_count, 0)

    def test_unlike_post(self):
        """Test unliking a post."""
        # Like first
        like_post(self.user2, self.post.id)
        
        # Unlike
        success, message, like_count = unlike_post(self.user2, self.post.id)
        
        self.assertTrue(success)
        self.assertEqual(like_count, 0)
        self.assertFalse(PostLike.objects.filter(user=self.user2, post=self.post).exists())

    def test_toggle_post_like(self):
        """Test toggling like on a post."""
        # First toggle: like
        success1, _, count1 = toggle_post_like(self.user2, self.post.id)
        self.assertTrue(success1)
        self.assertEqual(count1, 1)
        
        # Second toggle: unlike
        success2, _, count2 = toggle_post_like(self.user2, self.post.id)
        self.assertTrue(success2)
        self.assertEqual(count2, 0)
        
        # Third toggle: like again
        success3, _, count3 = toggle_post_like(self.user2, self.post.id)
        self.assertTrue(success3)
        self.assertEqual(count3, 1)


class PostLikeUniqueConstraintTest(TestCase):
    """Test the database unique constraint on likes."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.post = Post.objects.create(
            author=self.user,
            content='Test post'
        )

    def test_unique_constraint_prevents_duplicates(self):
        """Test that the unique constraint prevents duplicate likes at DB level."""
        PostLike.objects.create(user=self.user, post=self.post)
        
        with self.assertRaises(IntegrityError):
            PostLike.objects.create(user=self.user, post=self.post)
