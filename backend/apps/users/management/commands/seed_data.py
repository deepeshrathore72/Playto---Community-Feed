"""
Management command to seed the database with test data.
"""
import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.users.models import User, KarmaTransaction
from apps.posts.models import Post
from apps.comments.models import Comment
from apps.likes.models import PostLike, CommentLike


class Command(BaseCommand):
    help = 'Seed the database with test data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Number of users to create'
        )
        parser.add_argument(
            '--posts',
            type=int,
            default=20,
            help='Number of posts to create'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            KarmaTransaction.objects.all().delete()
            CommentLike.objects.all().delete()
            PostLike.objects.all().delete()
            Comment.objects.all().delete()
            Post.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()

        num_users = options['users']
        num_posts = options['posts']

        self.stdout.write(f'Creating {num_users} users...')
        users = self._create_users(num_users)

        self.stdout.write(f'Creating {num_posts} posts...')
        posts = self._create_posts(users, num_posts)

        self.stdout.write('Creating comments...')
        comments = self._create_comments(users, posts)

        self.stdout.write('Creating likes and karma...')
        self._create_likes(users, posts, comments)

        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))

    def _create_users(self, count):
        users = []
        usernames = [
            'alice', 'bob', 'charlie', 'diana', 'eve',
            'frank', 'grace', 'henry', 'iris', 'jack',
            'kate', 'leo', 'maya', 'noah', 'olivia'
        ]
        
        for i, username in enumerate(usernames[:count]):
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@example.com',
                    'bio': f'Hello, I am {username.title()}!',
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            users.append(user)
        
        return users

    def _create_posts(self, users, count):
        posts = []
        post_contents = [
            "Just discovered this amazing community! 🎉",
            "Working on a new project. Can't wait to share it!",
            "Anyone else excited about the new features?",
            "Hot take: tabs are better than spaces. Fight me.",
            "Finally finished my side project after 6 months!",
            "Learning something new every day 📚",
            "Best practices for code reviews - what are yours?",
            "The importance of documentation cannot be overstated.",
            "Just deployed my first app to production! 🚀",
            "What's everyone working on this weekend?",
            "Productivity tip: use keyboard shortcuts!",
            "Clean code is not about being clever.",
            "Remember to take breaks while coding!",
            "Just refactored 1000 lines into 100. Feels good.",
            "Open source contributions are the best way to learn.",
            "Who else loves pair programming?",
            "Debugging is like being a detective in a crime movie.",
            "Coffee + Code = Perfect Morning ☕",
            "Version control saved my life today.",
            "Learning to love writing tests.",
        ]
        
        for i in range(count):
            content = post_contents[i % len(post_contents)]
            author = random.choice(users)
            post = Post.objects.create(
                author=author,
                content=content,
            )
            posts.append(post)
        
        return posts

    def _create_comments(self, users, posts):
        comments = []
        comment_texts = [
            "Great post! 👍",
            "I totally agree with this.",
            "Interesting perspective!",
            "Can you elaborate more on this?",
            "This is exactly what I needed to hear.",
            "Thanks for sharing!",
            "I have a different opinion on this...",
            "Love this! 🎉",
            "Very helpful, thank you!",
            "This made my day!",
        ]
        
        reply_texts = [
            "I agree!",
            "Good point!",
            "Thanks for the reply!",
            "That makes sense.",
            "Interesting take!",
        ]
        
        for post in posts:
            # Create 2-5 top-level comments per post
            num_comments = random.randint(2, 5)
            for _ in range(num_comments):
                comment = Comment.objects.create(
                    post=post,
                    author=random.choice(users),
                    content=random.choice(comment_texts),
                )
                comments.append(comment)
                
                # Create 0-3 replies to this comment
                num_replies = random.randint(0, 3)
                for _ in range(num_replies):
                    reply = Comment.objects.create(
                        post=post,
                        parent=comment,
                        author=random.choice(users),
                        content=random.choice(reply_texts),
                    )
                    comments.append(reply)
                    
                    # Occasionally create nested replies
                    if random.random() < 0.3:
                        nested_reply = Comment.objects.create(
                            post=post,
                            parent=reply,
                            author=random.choice(users),
                            content=random.choice(reply_texts),
                        )
                        comments.append(nested_reply)
        
        return comments

    def _create_likes(self, users, posts, comments):
        now = timezone.now()
        
        # Like some posts
        for post in posts:
            # Each post gets 0-5 likes
            likers = random.sample(users, min(random.randint(0, 5), len(users)))
            for user in likers:
                if user.id != post.author_id:
                    try:
                        PostLike.objects.create(user=user, post=post)
                        post.like_count += 1
                        
                        # Create karma transaction with random time in last 48 hours
                        hours_ago = random.uniform(0, 48)
                        KarmaTransaction.objects.create(
                            user=post.author,
                            karma_type=KarmaTransaction.KARMA_TYPE_POST_LIKE,
                            points=KarmaTransaction.KARMA_POINTS[KarmaTransaction.KARMA_TYPE_POST_LIKE],
                            content_type='post',
                            object_id=post.id,
                            created_at=now - timedelta(hours=hours_ago)
                        )
                    except Exception:
                        pass
            post.save()
        
        # Like some comments
        for comment in comments:
            # Each comment gets 0-3 likes
            likers = random.sample(users, min(random.randint(0, 3), len(users)))
            for user in likers:
                if user.id != comment.author_id:
                    try:
                        CommentLike.objects.create(user=user, comment=comment)
                        comment.like_count += 1
                        
                        hours_ago = random.uniform(0, 48)
                        KarmaTransaction.objects.create(
                            user=comment.author,
                            karma_type=KarmaTransaction.KARMA_TYPE_COMMENT_LIKE,
                            points=KarmaTransaction.KARMA_POINTS[KarmaTransaction.KARMA_TYPE_COMMENT_LIKE],
                            content_type='comment',
                            object_id=comment.id,
                            created_at=now - timedelta(hours=hours_ago)
                        )
                    except Exception:
                        pass
            comment.save()
