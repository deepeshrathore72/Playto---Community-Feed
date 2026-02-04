"""
Leaderboard service module.

This module calculates karma rankings dynamically from the KarmaTransaction table.
NO daily karma is stored on the User model - it's always computed on-demand.

The key query aggregates karma points from the last 24 hours, groups by user,
and orders by total points descending.
"""
from datetime import timedelta
from django.db.models import Sum
from django.utils import timezone
from apps.users.models import KarmaTransaction, User


def get_leaderboard(limit=5, hours=24):
    """
    Get the top users by karma earned in the specified time period.
    
    This function performs a single efficient database query that:
    1. Filters KarmaTransaction by created_at >= 24 hours ago
    2. Groups by user_id
    3. Sums the points for each user
    4. Orders by total points descending
    5. Limits to top N users
    
    The SQL equivalent:
    
    SELECT 
        user_id,
        SUM(points) as total_karma
    FROM karma_transactions
    WHERE created_at >= NOW() - INTERVAL '24 hours'
    GROUP BY user_id
    ORDER BY total_karma DESC
    LIMIT 5;
    
    Args:
        limit: Number of top users to return (default: 5)
        hours: Time window in hours (default: 24)
    
    Returns:
        List of dicts with user info and karma
    """
    # Calculate the cutoff time
    cutoff_time = timezone.now() - timedelta(hours=hours)
    
    # Aggregate karma by user in the time window
    # This is a single efficient query with GROUP BY
    karma_rankings = (
        KarmaTransaction.objects
        .filter(created_at__gte=cutoff_time)
        .values('user_id')
        .annotate(total_karma=Sum('points'))
        .order_by('-total_karma')
        [:limit]
    )
    
    if not karma_rankings:
        return []
    
    # Get user details for the top users
    user_ids = [entry['user_id'] for entry in karma_rankings]
    users_by_id = {
        user.id: user 
        for user in User.objects.filter(id__in=user_ids)
    }
    
    # Build the result list
    result = []
    for rank, entry in enumerate(karma_rankings, start=1):
        user = users_by_id.get(entry['user_id'])
        if user:
            result.append({
                'rank': rank,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'avatar_url': user.avatar_url,
                },
                'karma_24h': entry['total_karma'],
            })
    
    return result


def get_user_karma_breakdown(user_id, hours=24):
    """
    Get detailed karma breakdown for a specific user.
    
    Returns karma earned from post likes and comment likes separately.
    """
    cutoff_time = timezone.now() - timedelta(hours=hours)
    
    breakdown = (
        KarmaTransaction.objects
        .filter(user_id=user_id, created_at__gte=cutoff_time)
        .values('karma_type')
        .annotate(total=Sum('points'))
    )
    
    result = {
        'post_likes_karma': 0,
        'comment_likes_karma': 0,
        'total_karma_24h': 0,
    }
    
    for entry in breakdown:
        if entry['karma_type'] == KarmaTransaction.KARMA_TYPE_POST_LIKE:
            result['post_likes_karma'] = entry['total']
        elif entry['karma_type'] == KarmaTransaction.KARMA_TYPE_COMMENT_LIKE:
            result['comment_likes_karma'] = entry['total']
    
    result['total_karma_24h'] = (
        result['post_likes_karma'] + result['comment_likes_karma']
    )
    
    return result


def get_user_total_karma(user_id):
    """
    Get total all-time karma for a user.
    """
    total = (
        KarmaTransaction.objects
        .filter(user_id=user_id)
        .aggregate(total=Sum('points'))
    )
    return total['total'] or 0
