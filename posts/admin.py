from django.contrib import admin
from .models import Post, PostMedia, UserInteraction

class MediaInline(admin.TabularInline):
    model = PostMedia
    extra = 1

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    inlines = [MediaInline]
    list_display = ['id', 'content', 'content', 'created_at', 'updated_at']


admin.site.register(UserInteraction)