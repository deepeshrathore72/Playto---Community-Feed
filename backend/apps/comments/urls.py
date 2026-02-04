from django.urls import path
from . import views

app_name = 'comments'

urlpatterns = [
    path('', views.CommentCreateView.as_view(), name='comment-create'),
    path('<int:pk>/', views.CommentDetailView.as_view(), name='comment-detail'),
    path('post/<int:post_id>/', views.PostCommentsView.as_view(), name='post-comments'),
]
