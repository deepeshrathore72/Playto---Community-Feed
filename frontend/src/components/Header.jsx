import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { User, LogOut, ChevronDown } from 'lucide-react';

export default function Header() {
  const { user, users, login, logout, isAuthenticated } = useAuth();
  const [showDropdown, setShowDropdown] = useState(false);

  // Ensure users is always an array
  const usersList = Array.isArray(users) ? users : [];

  const handleUserSelect = async (username) => {
    await login(username);
    setShowDropdown(false);
  };

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center">
              <span className="text-white font-bold text-lg">C</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">Community Feed</h1>
              <p className="text-xs text-gray-500">Threaded Discussions</p>
            </div>
          </div>

          <div className="relative">
            {isAuthenticated ? (
              <div className="flex items-center gap-3">
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900">{user.username}</p>
                  <p className="text-xs text-gray-500">Logged in</p>
                </div>
                <button
                  onClick={logout}
                  className="p-2 text-gray-500 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                  title="Logout"
                >
                  <LogOut size={20} />
                </button>
              </div>
            ) : (
              <div className="relative">
                <button
                  onClick={() => setShowDropdown(!showDropdown)}
                  className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
                >
                  <User size={18} />
                  <span>Login</span>
                  <ChevronDown size={16} />
                </button>

                {showDropdown && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
                    <p className="px-4 py-2 text-xs text-gray-500 border-b border-gray-100">
                      Select a user:
                    </p>
                    {usersList.length === 0 ? (
                      <p className="px-4 py-2 text-xs text-gray-400 text-center">
                        No users available
                      </p>
                    ) : (
                      usersList.map((u) => (
                        <button
                          key={u.id}
                          onClick={() => handleUserSelect(u.username)}
                          className="w-full text-left px-4 py-2 hover:bg-gray-50 text-sm text-gray-700"
                        >
                          {u.username}
                        </button>
                      ))
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
