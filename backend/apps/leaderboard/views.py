from rest_framework.response import Response
from rest_framework.views import APIView
from . import services


class LeaderboardView(APIView):
    """
    Get the karma leaderboard for the last 24 hours.
    
    GET /api/leaderboard/
    
    Returns the top 5 users by karma earned in the last 24 hours.
    Karma is calculated dynamically from KarmaTransaction records,
    NOT from a stored field on the User model.
    
    Response format:
    {
        "leaderboard": [
            {
                "rank": 1,
                "user": {
                    "id": 1,
                    "username": "john",
                    "avatar_url": null
                },
                "karma_24h": 50
            },
            ...
        ]
    }
    """

    def get(self, request):
        # Get optional parameters
        limit = int(request.query_params.get('limit', 5))
        hours = int(request.query_params.get('hours', 24))
        
        # Clamp values to reasonable ranges
        limit = min(max(limit, 1), 100)
        hours = min(max(hours, 1), 168)  # Max 1 week
        
        leaderboard = services.get_leaderboard(limit=limit, hours=hours)
        
        return Response({
            'leaderboard': leaderboard,
            'time_window_hours': hours,
        })


class UserKarmaView(APIView):
    """
    Get karma details for a specific user.
    
    GET /api/leaderboard/user/<user_id>/
    """

    def get(self, request, user_id):
        hours = int(request.query_params.get('hours', 24))
        hours = min(max(hours, 1), 168)
        
        breakdown = services.get_user_karma_breakdown(user_id, hours=hours)
        total_karma = services.get_user_total_karma(user_id)
        
        return Response({
            'user_id': user_id,
            'karma_24h': breakdown,
            'total_karma_all_time': total_karma,
        })
