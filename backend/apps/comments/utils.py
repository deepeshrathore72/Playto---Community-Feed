"""
Utility functions for building comment trees efficiently.

The key insight is that we fetch ALL comments for a post in ONE query,
then build the tree structure in Python. This avoids the N+1 problem
where each comment would trigger a query for its replies.
"""
from collections import defaultdict


def build_comment_tree(comments, serializer_class, context):
    """
    Build a nested comment tree from a flat list of comments.
    
    This function:
    1. Takes a flat list of all comments for a post (fetched in ONE query)
    2. Organizes them into a tree structure in memory (O(n) time)
    3. Returns serialized top-level comments with nested replies
    
    Args:
        comments: QuerySet or list of Comment objects (already fetched)
        serializer_class: The serializer class to use
        context: Serializer context (contains request, etc.)
    
    Returns:
        List of serialized top-level comments with nested 'replies'
    
    Time Complexity: O(n) where n is the number of comments
    Space Complexity: O(n) for the lookup dictionaries
    """
    if not comments:
        return []
    
    # Build lookup structures
    # parent_to_children: maps parent_id -> list of child comments
    # comment_by_id: maps comment_id -> comment object
    parent_to_children = defaultdict(list)
    comment_by_id = {}
    
    for comment in comments:
        comment_by_id[comment.id] = comment
        parent_id = comment.parent_id
        parent_to_children[parent_id].append(comment)
    
    def serialize_comment_with_replies(comment, depth_limit=10):
        """
        Recursively serialize a comment and its replies.
        
        We limit depth to prevent infinite recursion and keep responses manageable.
        """
        # Count direct replies
        direct_replies = parent_to_children.get(comment.id, [])
        comment._reply_count = len(direct_replies)
        
        # Build replies data (recursive, but using pre-fetched data)
        if comment.depth < depth_limit:
            comment._replies_data = [
                serialize_comment_with_replies(reply, depth_limit)
                for reply in sorted(direct_replies, key=lambda x: x.created_at)
            ]
        else:
            comment._replies_data = []
        
        # Serialize this comment
        serializer = serializer_class(comment, context=context)
        return serializer.data
    
    # Get top-level comments (parent_id = None)
    top_level_comments = parent_to_children.get(None, [])
    
    # Sort by created_at and serialize with nested replies
    result = [
        serialize_comment_with_replies(comment)
        for comment in sorted(top_level_comments, key=lambda x: x.created_at)
    ]
    
    return result


def get_flat_comment_list(comments, serializer_class, context):
    """
    Alternative: Return a flat list with parent references.
    Useful for clients that want to build the tree themselves.
    """
    for comment in comments:
        # Count replies
        reply_count = sum(1 for c in comments if c.parent_id == comment.id)
        comment._reply_count = reply_count
        comment._replies_data = []  # Don't nest, let client build tree
    
    serializer = serializer_class(comments, many=True, context=context)
    return serializer.data
