"""
URL configuration for Community Feed project.
"""
from django.contrib import admin
from django.urls import path, include
from apps.users.views_health import HealthCheckView
from apps.users.views_diagnostic import diagnostic_view

urlpatterns = [
    path('', diagnostic_view, name='diagnostic'),  # Simple root endpoint
    path('admin/', admin.site.urls),
    path('api/health/', HealthCheckView.as_view(), name='health-check'),
    path('api/users/', include('apps.users.urls')),
    path('api/posts/', include('apps.posts.urls')),
    path('api/comments/', include('apps.comments.urls')),
    path('api/likes/', include('apps.likes.urls')),
    path('api/leaderboard/', include('apps.leaderboard.urls')),
]
