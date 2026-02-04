"""
Tests for the leaderboard calculation logic.

These tests verify that:
1. Karma is calculated correctly from KarmaTransaction records
2. Only karma from the last 24 hours is counted
3. The ranking order is correct
"""
from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from apps.users.models import User, KarmaTransaction
from apps.leaderboard.services import get_leaderboard, get_user_karma_breakdown


class LeaderboardCalculationTests(TestCase):
    """Test the leaderboard calculation logic."""

    def setUp(self):
        """Create test users."""
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
        self.user3 = User.objects.create_user(
            username='user3',
            email='user3@test.com',
            password='testpass123'
        )

    def test_leaderboard_with_no_karma(self):
        """Test leaderboard when no karma transactions exist."""
        leaderboard = get_leaderboard()
        self.assertEqual(leaderboard, [])

    def test_leaderboard_ranking_order(self):
        """Test that users are ranked by karma in descending order."""
        now = timezone.now()
        
        # User1: 10 karma (2 post likes)
        for i in range(2):
            KarmaTransaction.objects.create(
                user=self.user1,
                karma_type=KarmaTransaction.KARMA_TYPE_POST_LIKE,
                points=5,
                content_type='post',
                object_id=i + 1
            )
        
        # User2: 15 karma (3 post likes)
        for i in range(3):
            KarmaTransaction.objects.create(
                user=self.user2,
                karma_type=KarmaTransaction.KARMA_TYPE_POST_LIKE,
                points=5,
                content_type='post',
                object_id=i + 1
            )
        
        # User3: 3 karma (3 comment likes)
        for i in range(3):
            KarmaTransaction.objects.create(
                user=self.user3,
                karma_type=KarmaTransaction.KARMA_TYPE_COMMENT_LIKE,
                points=1,
                content_type='comment',
                object_id=i + 1
            )
        
        leaderboard = get_leaderboard()
        
        # Check ranking order
        self.assertEqual(len(leaderboard), 3)
        self.assertEqual(leaderboard[0]['user']['username'], 'user2')  # 15 karma
        self.assertEqual(leaderboard[0]['karma_24h'], 15)
        self.assertEqual(leaderboard[1]['user']['username'], 'user1')  # 10 karma
        self.assertEqual(leaderboard[1]['karma_24h'], 10)
        self.assertEqual(leaderboard[2]['user']['username'], 'user3')  # 3 karma
        self.assertEqual(leaderboard[2]['karma_24h'], 3)

    def test_leaderboard_excludes_old_karma(self):
        """Test that karma older than 24 hours is not counted."""
        now = timezone.now()
        
        # User1: Recent karma (should be counted)
        KarmaTransaction.objects.create(
            user=self.user1,
            karma_type=KarmaTransaction.KARMA_TYPE_POST_LIKE,
            points=5,
            content_type='post',
            object_id=1
        )
        
        # User2: Old karma (should NOT be counted)
        old_transaction = KarmaTransaction.objects.create(
            user=self.user2,
            karma_type=KarmaTransaction.KARMA_TYPE_POST_LIKE,
            points=5,
            content_type='post',
            object_id=1
        )
        # Manually set old timestamp (25 hours ago)
        old_transaction.created_at = now - timedelta(hours=25)
        old_transaction.save()
        
        leaderboard = get_leaderboard()
        
        # Only user1 should appear (user2's karma is too old)
        self.assertEqual(len(leaderboard), 1)
        self.assertEqual(leaderboard[0]['user']['username'], 'user1')
        self.assertEqual(leaderboard[0]['karma_24h'], 5)

    def test_leaderboard_limit(self):
        """Test that leaderboard respects the limit parameter."""
        # Create karma for all users
        for user in [self.user1, self.user2, self.user3]:
            KarmaTransaction.objects.create(
                user=user,
                karma_type=KarmaTransaction.KARMA_TYPE_POST_LIKE,
                points=5,
                content_type='post',
                object_id=1
            )
        
        leaderboard = get_leaderboard(limit=2)
        self.assertEqual(len(leaderboard), 2)

    def test_karma_breakdown_calculation(self):
        """Test the karma breakdown for a user."""
        # Create mixed karma types
        KarmaTransaction.objects.create(
            user=self.user1,
            karma_type=KarmaTransaction.KARMA_TYPE_POST_LIKE,
            points=5,
            content_type='post',
            object_id=1
        )
        KarmaTransaction.objects.create(
            user=self.user1,
            karma_type=KarmaTransaction.KARMA_TYPE_POST_LIKE,
            points=5,
            content_type='post',
            object_id=2
        )
        KarmaTransaction.objects.create(
            user=self.user1,
            karma_type=KarmaTransaction.KARMA_TYPE_COMMENT_LIKE,
            points=1,
            content_type='comment',
            object_id=1
        )
        
        breakdown = get_user_karma_breakdown(self.user1.id)
        
        self.assertEqual(breakdown['post_likes_karma'], 10)
        self.assertEqual(breakdown['comment_likes_karma'], 1)
        self.assertEqual(breakdown['total_karma_24h'], 11)

    def test_karma_points_values(self):
        """Test that karma point values are correct."""
        self.assertEqual(
            KarmaTransaction.KARMA_POINTS[KarmaTransaction.KARMA_TYPE_POST_LIKE],
            5
        )
        self.assertEqual(
            KarmaTransaction.KARMA_POINTS[KarmaTransaction.KARMA_TYPE_COMMENT_LIKE],
            1
        )


class LeaderboardAPITests(TestCase):
    """Test the leaderboard API endpoints."""

    def setUp(self):
        """Create test user with karma."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        KarmaTransaction.objects.create(
            user=self.user,
            karma_type=KarmaTransaction.KARMA_TYPE_POST_LIKE,
            points=5,
            content_type='post',
            object_id=1
        )

    def test_leaderboard_endpoint(self):
        """Test the leaderboard API endpoint."""
        response = self.client.get('/api/leaderboard/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('leaderboard', response.json())
        self.assertIn('time_window_hours', response.json())
        
        leaderboard = response.json()['leaderboard']
        self.assertEqual(len(leaderboard), 1)
        self.assertEqual(leaderboard[0]['user']['username'], 'testuser')
        self.assertEqual(leaderboard[0]['karma_24h'], 5)

    def test_user_karma_endpoint(self):
        """Test the user karma API endpoint."""
        response = self.client.get(f'/api/leaderboard/user/{self.user.id}/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data['user_id'], self.user.id)
        self.assertEqual(data['karma_24h']['total_karma_24h'], 5)
