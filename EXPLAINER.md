# EXPLAINER.md - Technical Deep Dive

This document explains the key technical decisions and implementations in the Community Feed project.

---

## 1. The Tree: Nested Comments Implementation

### Database Model

I used the **Adjacency List** model for storing threaded comments. Each comment has:
- `post_id`: Reference to the parent post (all comments, regardless of nesting level)
- `parent_id`: Reference to the parent comment (NULL for top-level comments)
- `depth`: Pre-calculated nesting depth (0 for top-level, incremented for each level)

```python
class Comment(models.Model):
    post = models.ForeignKey('posts.Post', on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    depth = models.PositiveSmallIntegerField(default=0)
    # ... other fields
```

### Why Adjacency List over MPTT or Nested Sets?

1. **Simplicity**: Adjacency list is straightforward to understand and maintain
2. **Write Performance**: No need to update multiple rows when inserting a comment
3. **Sufficient for our use case**: We always fetch ALL comments for a post at once, so we can build the tree in Python

### Solving the N+1 Problem

The naive approach would trigger N queries (one per comment to fetch replies):

```python
# ❌ BAD: N+1 queries
for comment in comments:
    replies = comment.replies.all()  # Query per comment!
```

**My Solution**: Fetch ALL comments in ONE query, then build the tree in Python.

```python
# ✅ GOOD: Single query + O(n) Python processing
def build_comment_tree(comments, serializer_class, context):
    # Build lookup structures
    parent_to_children = defaultdict(list)
    comment_by_id = {}
    
    for comment in comments:
        comment_by_id[comment.id] = comment
        parent_to_children[comment.parent_id].append(comment)
    
    # Recursively serialize with nested replies
    def serialize_comment_with_replies(comment, depth_limit=10):
        direct_replies = parent_to_children.get(comment.id, [])
        comment._reply_count = len(direct_replies)
        comment._replies_data = [
            serialize_comment_with_replies(reply)
            for reply in sorted(direct_replies, key=lambda x: x.created_at)
        ]
        return serializer_class(comment, context=context).data
    
    # Get top-level comments and build tree
    top_level = parent_to_children.get(None, [])
    return [serialize_comment_with_replies(c) for c in top_level]
```

**Query Count**: Exactly 2-3 queries regardless of comment count:
1. Fetch all comments with `select_related('author')` - single JOIN
2. Prefetch user's likes (if logged in) - single query
3. Build tree in Python - O(n) time, O(n) space

---

## 2. The Math: Leaderboard Query

### The Requirement
Calculate karma earned in the **last 24 hours only**, dynamically from transaction history.

### The Schema

```python
class KarmaTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    karma_type = models.CharField(max_length=20)  # 'post_like' or 'comment_like'
    points = models.IntegerField()  # 5 for post, 1 for comment
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
```

### The Query (Django ORM)

```python
def get_leaderboard(limit=5, hours=24):
    cutoff_time = timezone.now() - timedelta(hours=hours)
    
    karma_rankings = (
        KarmaTransaction.objects
        .filter(created_at__gte=cutoff_time)        # Last 24 hours
        .values('user_id')                           # GROUP BY user_id
        .annotate(total_karma=Sum('points'))         # SUM(points)
        .order_by('-total_karma')                    # ORDER BY total_karma DESC
        [:limit]                                     # LIMIT 5
    )
    
    return karma_rankings
```

### Equivalent SQL

```sql
SELECT 
    user_id,
    SUM(points) as total_karma
FROM karma_transactions
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY user_id
ORDER BY total_karma DESC
LIMIT 5;
```

### Why This Approach?

1. **No Denormalization**: We don't store daily karma on the User model
2. **Accurate**: Always reflects actual transaction history
3. **Efficient**: Single query with proper indexes on `(user_id, created_at)`
4. **Flexible**: Can easily change time window via parameter

---

## 3. Concurrency: Race Condition Prevention

### The Problem
Two simultaneous "like" requests could:
1. Both read "not liked"
2. Both create like records
3. Both increment count
4. Result: 2 likes instead of 1, inflated karma

### The Solution: Multi-Layer Defense

#### Layer 1: Database Unique Constraint
```python
class PostLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ['user', 'post']  # DB-level constraint
```

Even if two requests pass Python checks simultaneously, the database will reject the duplicate.

#### Layer 2: Atomic Transactions with Row Locking
```python
def like_post(user, post_id):
    try:
        with transaction.atomic():
            # Lock the post row to prevent concurrent modifications
            post = Post.objects.select_for_update().get(id=post_id)
            
            # Try to create - unique constraint prevents duplicates
            PostLike.objects.create(user=user, post=post)
            
            # Use F() expression for atomic increment
            Post.objects.filter(id=post_id).update(
                like_count=F('like_count') + 1
            )
            
            # Create karma transaction
            KarmaTransaction.objects.create(...)
            
    except IntegrityError:
        # Already liked - unique constraint violation
        return False, "Already liked"
```

#### Layer 3: F() Expressions for Count Updates
```python
# ❌ BAD: Race condition
post.like_count += 1
post.save()

# ✅ GOOD: Atomic at database level
Post.objects.filter(id=post_id).update(like_count=F('like_count') + 1)
```

The F() expression generates SQL like:
```sql
UPDATE posts SET like_count = like_count + 1 WHERE id = ?
```

This is atomic at the database level - no Python-side read-modify-write.

---

## 4. The AI Audit

### Example: AI's Initial Leaderboard Implementation Was Buggy

**The Bug**: When I first asked for a leaderboard implementation, the AI generated code that would count ALL karma, not just the last 24 hours:

```python
# ❌ AI's buggy initial code
def get_leaderboard():
    return User.objects.annotate(
        total_karma=Sum('karma_transactions__points')
    ).order_by('-total_karma')[:5]
```

This ignores the 24-hour constraint entirely!

**The Fix**: I added the proper time filter:

```python
# ✅ Corrected implementation
def get_leaderboard(limit=5, hours=24):
    cutoff_time = timezone.now() - timedelta(hours=hours)
    
    karma_rankings = (
        KarmaTransaction.objects
        .filter(created_at__gte=cutoff_time)  # THIS WAS MISSING
        .values('user_id')
        .annotate(total_karma=Sum('points'))
        .order_by('-total_karma')
        [:limit]
    )
```

### Example 2: AI's N+1 in Comment Serialization

**The Bug**: AI initially suggested using a recursive serializer field:

```python
# ❌ AI's buggy approach
class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()
    
    def get_replies(self, obj):
        # This triggers a query for EACH comment!
        replies = obj.replies.all()
        return CommentSerializer(replies, many=True).data
```

This creates N+1 queries because each comment fetches its own replies.

**The Fix**: Fetch all comments once, build tree in Python:

```python
# ✅ Corrected approach in views.py
comments = list(Comment.objects.filter(post=post).select_related('author'))
# Build tree in memory - O(n)
comment_tree = build_comment_tree(comments, CommentSerializer, context)
```

### Lesson Learned
AI is excellent for boilerplate and common patterns, but complex aggregations and performance-critical code require human review. The 24-hour filter and N+1 prevention were both missed by initial AI suggestions.

---

## 5. Additional Optimizations

### Database Indexes
```python
class KarmaTransaction(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['user', 'created_at']),  # For user karma queries
            models.Index(fields=['created_at']),          # For leaderboard
        ]
```

### Prefetching User Likes
For the "is_liked_by_user" field, we prefetch only the current user's likes:

```python
queryset = Post.objects.select_related('author').prefetch_related(
    Prefetch(
        'post_likes',
        queryset=PostLike.objects.filter(user_id=current_user_id),
        to_attr='prefetched_likes'  # Store in attribute, not queryset
    )
)
```

This results in exactly 2 queries regardless of the number of posts.

---

## Summary

| Challenge | Solution |
|-----------|----------|
| N+1 Comments | Fetch all, build tree in Python O(n) |
| 24h Leaderboard | Aggregate query with time filter |
| Double-likes | DB unique constraint + atomic transactions |
| Like count race | F() expressions for atomic updates |
| User likes check | Prefetch only current user's likes |
