import { useState } from 'react';
import { formatDistanceToNow } from 'date-fns';
import { useAuth } from '../context/AuthContext';
import { likesApi } from '../api';
import { Heart, MessageCircle, ChevronDown, ChevronUp } from 'lucide-react';
import CreateComment from './CreateComment';

export default function CommentThread({ comment, postId, onReplyCreated, depth = 0 }) {
  const { isAuthenticated } = useAuth();
  const [isLiked, setIsLiked] = useState(comment.is_liked_by_user);
  const [likeCount, setLikeCount] = useState(comment.like_count);
  const [likeLoading, setLikeLoading] = useState(false);
  const [showReplyForm, setShowReplyForm] = useState(false);
  const [showReplies, setShowReplies] = useState(true);

  const handleLike = async () => {
    if (!isAuthenticated || likeLoading) return;

    setLikeLoading(true);
    try {
      const response = await likesApi.toggleCommentLike(comment.id);
      setIsLiked(response.data.is_liked);
      setLikeCount(response.data.like_count);
    } catch (error) {
      console.error('Failed to toggle like:', error);
    } finally {
      setLikeLoading(false);
    }
  };

  const handleReplyCreated = (newReply) => {
    setShowReplyForm(false);
    onReplyCreated?.(newReply);
  };

  const timeAgo = formatDistanceToNow(new Date(comment.created_at), { addSuffix: true });
  const hasReplies = comment.replies && comment.replies.length > 0;
  
  // Limit nesting depth for display (10 levels max)
  const maxDepth = 10;
  const shouldNest = depth < maxDepth;

  return (
    <div className={`${depth > 0 ? 'ml-6 pl-4 border-l-2 border-gray-200' : ''}`}>
      <div className="bg-white rounded-lg p-3">
        {/* Author info */}
        <div className="flex items-center gap-2 mb-2">
          <div className="w-7 h-7 bg-gradient-to-br from-gray-400 to-gray-600 rounded-full flex items-center justify-center text-white text-xs font-semibold">
            {comment.author.username.charAt(0).toUpperCase()}
          </div>
          <span className="font-medium text-sm text-gray-900">{comment.author.username}</span>
          <span className="text-xs text-gray-400">•</span>
          <span className="text-xs text-gray-500">{timeAgo}</span>
        </div>

        {/* Content */}
        <p className="text-gray-800 text-sm leading-relaxed mb-2">{comment.content}</p>

        {/* Actions */}
        <div className="flex items-center gap-3 text-xs">
          <button
            onClick={handleLike}
            disabled={!isAuthenticated || likeLoading}
            className={`flex items-center gap-1 px-2 py-1 rounded transition-colors ${
              isLiked
                ? 'text-red-500 bg-red-50 hover:bg-red-100'
                : 'text-gray-500 hover:bg-gray-100'
            } disabled:opacity-50 disabled:cursor-not-allowed`}
          >
            <Heart size={14} className={isLiked ? 'fill-current' : ''} />
            <span>{likeCount}</span>
          </button>

          {isAuthenticated && shouldNest && (
            <button
              onClick={() => setShowReplyForm(!showReplyForm)}
              className="flex items-center gap-1 px-2 py-1 rounded text-gray-500 hover:bg-gray-100 transition-colors"
            >
              <MessageCircle size={14} />
              <span>Reply</span>
            </button>
          )}

          {hasReplies && (
            <button
              onClick={() => setShowReplies(!showReplies)}
              className="flex items-center gap-1 px-2 py-1 rounded text-primary-500 hover:bg-primary-50 transition-colors"
            >
              {showReplies ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
              <span>
                {showReplies ? 'Hide' : 'Show'} {comment.replies.length}{' '}
                {comment.replies.length === 1 ? 'reply' : 'replies'}
              </span>
            </button>
          )}
        </div>
      </div>

      {/* Reply form */}
      {showReplyForm && (
        <div className="mt-2 ml-6">
          <CreateComment
            postId={postId}
            parentId={comment.id}
            onCommentCreated={handleReplyCreated}
            onCancel={() => setShowReplyForm(false)}
            placeholder={`Reply to ${comment.author.username}...`}
            compact
          />
        </div>
      )}

      {/* Nested replies */}
      {showReplies && hasReplies && (
        <div className="mt-2 space-y-2">
          {comment.replies.map((reply) => (
            <CommentThread
              key={reply.id}
              comment={reply}
              postId={postId}
              onReplyCreated={onReplyCreated}
              depth={depth + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
}
