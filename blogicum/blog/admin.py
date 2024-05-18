from django.contrib import admin

from .models import Category, Location, Post, Comment


@admin.register(Category, Location, Comment)
class PostInfoAdmin(admin.ModelAdmin):
    pass


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'comments_count')

    @admin.display(description='Количество комментариев')
    def comments_count(self, obj):
        return obj.comments.count()
