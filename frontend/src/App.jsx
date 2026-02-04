import { AuthProvider } from './context/AuthContext';
import Header from './components/Header';
import Feed from './components/Feed';
import Leaderboard from './components/Leaderboard';

function App() {
  return (
    <AuthProvider>
      <div className="min-h-screen bg-gray-50">
        <Header />
        
        <main className="max-w-6xl mx-auto px-4 py-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Main feed */}
            <div className="lg:col-span-2">
              <Feed />
            </div>
            
            {/* Sidebar */}
            <div className="space-y-4">
              <Leaderboard />
              
              {/* Info card */}
              <div className="bg-white rounded-xl border border-gray-200 p-4">
                <h3 className="font-semibold text-gray-900 mb-2">About</h3>
                <p className="text-sm text-gray-600 mb-3">
                  A community feed with threaded discussions and a dynamic karma-based leaderboard.
                </p>
                <div className="text-xs text-gray-500 space-y-1">
                  <p>🔥 Nested comments (like Reddit)</p>
                  <p>⚡ Real-time karma tracking</p>
                  <p>🏆 24-hour leaderboard</p>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </AuthProvider>
  );
}

export default App;
