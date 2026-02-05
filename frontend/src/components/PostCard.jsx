import { useState } from 'react';
import { formatDistanceToNow } from 'date-fns';
import { useAuth } from '../context/AuthContext';
import { likesApi, commentsApi } from '../api';
import { Heart, MessageCircle, ChevronDown, ChevronUp } from 'lucide-react';
import CommentThread from './CommentThread';
import CreateComment from './CreateComment';

export default function PostCard({ post, onUpdate }) {
  const { isAuthenticated } = useAuth();
  const [isLiked, setIsLiked] = useState(post.is_liked_by_user);
  const [likeCount, setLikeCount] = useState(post.like_count);
  const [likeLoading, setLikeLoading] = useState(false);
  const [showComments, setShowComments] = useState(false);
  const [comments, setComments] = useState([]);
  const [commentsLoading, setCommentsLoading] = useState(false);
  const [commentCount, setCommentCount] = useState(post.comment_count);

  const handleLike = async () => {
    if (!isAuthenticated || likeLoading) return;

    setLikeLoading(true);
    try {
      const response = await likesApi.togglePostLike(post.id);
      setIsLiked(response.data.is_liked);
      setLikeCount(response.data.like_count);
    } catch (error) {
      console.error('Failed to toggle like:', error);
    } finally {
      setLikeLoading(false);
    }
  };

  const toggleComments = async () => {
    if (showComments) {
      setShowComments(false);
      return;
    }

    setShowComments(true);
    setCommentsLoading(true);

    try {
      const response = await commentsApi.getByPost(post.id);
      setComments(Array.isArray(response.data.comments) ? response.data.comments : []);
    } catch (error) {
      console.error('Failed to load comments:', error);
      setComments([]);
    } finally {
      setCommentsLoading(false);
    }
  };

  const handleCommentCreated = (newComment) => {
    // Add the new comment to the appropriate place
    if (newComment.parent) {
      // It's a reply - need to update the tree
      // For simplicity, refresh the comments
      commentsApi.getByPost(post.id).then((response) => {
        setComments(Array.isArray(response.data.comments) ? response.data.comments : []);
      }).catch(() => {
        setComments([]);
      });
    } else {
      // It's a top-level comment
      setComments([...comments, { ...newComment, replies: [], reply_count: 0 }]);
    }
    setCommentCount((prev) => prev + 1);
  };

  const timeAgo = formatDistanceToNow(new Date(post.created_at), { addSuffix: true });

  return (
    <article className="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div className="p-4">
        {/* Author info */}
        <div className="flex items-center gap-3 mb-3">
          <div className="w-10 h-10 bg-gradient-to-br from-primary-400 to-primary-600 rounded-full flex items-center justify-center text-white font-semibold">
            {post.author.username.charAt(0).toUpperCase()}
          </div>
          <div>
            <p className="font-medium text-gray-900">{post.author.username}</p>
            <p className="text-xs text-gray-500">{timeAgo}</p>
          </div>
        </div>

        {/* Content */}
        <p className="text-gray-800 whitespace-pre-wrap leading-relaxed">{post.content}</p>
      </div>

      {/* Actions */}
      <div className="px-4 py-3 border-t border-gray-100 flex items-center gap-4">
        <button
          onClick={handleLike}
          disabled={!isAuthenticated || likeLoading}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-lg transition-colors ${
            isLiked
              ? 'text-red-500 bg-red-50 hover:bg-red-100'
              : 'text-gray-600 hover:bg-gray-100'
          } disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          <Heart size={18} className={isLiked ? 'fill-current' : ''} />
          <span className="text-sm font-medium">{likeCount}</span>
        </button>

        <button
          onClick={toggleComments}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-gray-600 hover:bg-gray-100 transition-colors"
        >
          <MessageCircle size={18} />
          <span className="text-sm font-medium">{commentCount}</span>
          {showComments ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </button>
      </div>

      {/* Comments section */}
      {showComments && (
        <div className="border-t border-gray-100 bg-gray-50">
          {isAuthenticated && (
            <div className="p-4 border-b border-gray-100 bg-white">
              <CreateComment postId={post.id} onCommentCreated={handleCommentCreated} />
            </div>
          )}

          <div className="p-4">
            {commentsLoading ? (
              <div className="text-center py-4">
                <div className="animate-spin w-6 h-6 border-2 border-primary-500 border-t-transparent rounded-full mx-auto"></div>
                <p className="text-gray-500 text-sm mt-2">Loading comments...</p>
              </div>
            ) : comments.length === 0 ? (
              <p className="text-gray-500 text-center py-4">
                No comments yet. Be the first to comment!
              </p>
            ) : (
              <div className="space-y-4">
                {comments.map((comment) => (
                  <CommentThread
                    key={comment.id}
                    comment={comment}
                    postId={post.id}
                    onReplyCreated={handleCommentCreated}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </article>
  );
}
