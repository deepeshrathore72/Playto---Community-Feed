import { useState, useEffect } from 'react';
import { leaderboardApi } from '../api';
import { Trophy, Star, TrendingUp } from 'lucide-react';

export default function Leaderboard() {
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLeaderboard();
    // Refresh every 30 seconds
    const interval = setInterval(fetchLeaderboard, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchLeaderboard = async () => {
    try {
      const response = await leaderboardApi.get(5, 24);
      setLeaderboard(Array.isArray(response.data.leaderboard) ? response.data.leaderboard : []);
    } catch (error) {
      console.error('Failed to fetch leaderboard:', error);
      setLeaderboard([]);
    } finally {
      setLoading(false);
    }
  };

  const getRankStyle = (rank) => {
    switch (rank) {
      case 1:
        return 'bg-gradient-to-r from-yellow-400 to-amber-500 text-white';
      case 2:
        return 'bg-gradient-to-r from-gray-300 to-gray-400 text-gray-800';
      case 3:
        return 'bg-gradient-to-r from-orange-400 to-orange-500 text-white';
      default:
        return 'bg-gray-100 text-gray-600';
    }
  };

  const getRankIcon = (rank) => {
    if (rank === 1) return <Trophy size={14} />;
    if (rank <= 3) return <Star size={14} />;
    return <span className="text-xs">{rank}</span>;
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-4">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/2 mb-4"></div>
          {[...Array(5)].map((_, i) => (
            <div key={i} className="flex items-center gap-3 py-3">
              <div className="w-8 h-8 bg-gray-200 rounded-full"></div>
              <div className="flex-1">
                <div className="h-4 bg-gray-200 rounded w-2/3 mb-1"></div>
                <div className="h-3 bg-gray-200 rounded w-1/3"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div className="bg-gradient-to-r from-primary-500 to-primary-600 px-4 py-3">
        <div className="flex items-center gap-2 text-white">
          <TrendingUp size={20} />
          <h2 className="font-semibold">Top 5 Users</h2>
        </div>
        <p className="text-primary-100 text-xs mt-1">Last 24 hours</p>
      </div>

      <div className="divide-y divide-gray-100">
        {leaderboard.length === 0 ? (
          <div className="px-4 py-8 text-center text-gray-500">
            <Trophy size={32} className="mx-auto mb-2 text-gray-300" />
            <p>No karma earned yet</p>
            <p className="text-xs mt-1">Start liking posts and comments!</p>
          </div>
        ) : (
          leaderboard.map((entry) => (
            <div
              key={entry.user.id}
              className="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 transition-colors"
            >
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${getRankStyle(
                  entry.rank
                )}`}
              >
                {getRankIcon(entry.rank)}
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-gray-900 truncate">
                  {entry.user.username}
                </p>
              </div>
              <div className="text-right">
                <p className="font-bold text-primary-600">{entry.karma_24h}</p>
                <p className="text-xs text-gray-500">karma</p>
              </div>
            </div>
          ))
        )}
      </div>

      <div className="px-4 py-2 bg-gray-50 border-t border-gray-100">
        <p className="text-xs text-gray-500 text-center">
          🎮 5 karma per post like • 1 karma per comment like
        </p>
      </div>
    </div>
  );
}
