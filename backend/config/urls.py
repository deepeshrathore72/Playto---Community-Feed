"""
URL configuration for Community Feed project.
"""
from django.contrib import admin
from django.urls import path, include
from apps.users.views_health import HealthCheckView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', HealthCheckView.as_view(), name='health-check'),
    path('api/users/', include('apps.users.urls')),
    path('api/posts/', include('apps.posts.urls')),
    path('api/comments/', include('apps.comments.urls')),
    path('api/likes/', include('apps.likes.urls')),
    path('api/leaderboard/', include('apps.leaderboard.urls')),
]
