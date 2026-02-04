from django.contrib import admin
from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'like_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['author__username', 'content']
    ordering = ['-created_at']
    readonly_fields = ['like_count', 'created_at', 'updated_at']
