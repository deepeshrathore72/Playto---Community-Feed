from django.urls import path
from . import views

app_name = 'likes'

urlpatterns = [
    path('post/<int:post_id>/toggle/', views.PostLikeToggleView.as_view(), name='post-like-toggle'),
    path('comment/<int:comment_id>/toggle/', views.CommentLikeToggleView.as_view(), name='comment-like-toggle'),
]
