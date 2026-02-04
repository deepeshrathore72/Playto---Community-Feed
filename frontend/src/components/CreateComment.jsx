import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { commentsApi } from '../api';
import { Send, X } from 'lucide-react';

export default function CreateComment({
  postId,
  parentId = null,
  onCommentCreated,
  onCancel,
  placeholder = 'Write a comment...',
  compact = false,
}) {
  const { isAuthenticated, user } = useAuth();
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!content.trim()) return;

    setLoading(true);
    setError('');

    try {
      const response = await commentsApi.create({
        post: postId,
        parent: parentId,
        content: content.trim(),
      });
      setContent('');
      onCommentCreated?.(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create comment');
    } finally {
      setLoading(false);
    }
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <form onSubmit={handleSubmit} className={compact ? '' : 'flex gap-3'}>
      {!compact && (
        <div className="w-8 h-8 bg-gradient-to-br from-primary-400 to-primary-600 rounded-full flex items-center justify-center text-white text-sm font-semibold flex-shrink-0">
          {user.username.charAt(0).toUpperCase()}
        </div>
      )}
      <div className="flex-1">
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder={placeholder}
          className={`w-full p-2 border border-gray-200 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm ${
            compact ? 'rows-2' : ''
          }`}
          rows={compact ? 2 : 2}
          maxLength={2000}
        />
        {error && <p className="text-red-500 text-xs mt-1">{error}</p>}
        <div className="flex items-center justify-end gap-2 mt-2">
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              className="flex items-center gap-1 px-3 py-1.5 text-gray-500 hover:bg-gray-100 rounded-lg text-sm transition-colors"
            >
              <X size={14} />
              <span>Cancel</span>
            </button>
          )}
          <button
            type="submit"
            disabled={!content.trim() || loading}
            className="flex items-center gap-1 px-3 py-1.5 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed text-sm transition-colors"
          >
            <Send size={14} />
            <span>{loading ? 'Posting...' : parentId ? 'Reply' : 'Comment'}</span>
          </button>
        </div>
      </div>
    </form>
  );
}
