from django.contrib import admin
from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'post', 'parent', 'depth', 'like_count', 'created_at']
    list_filter = ['created_at', 'depth']
    search_fields = ['author__username', 'content']
    ordering = ['-created_at']
    readonly_fields = ['like_count', 'depth', 'created_at', 'updated_at']
