from django.contrib import admin

from blogicum.constants import MAX_LEN_TEXT
from .models import Category, Comment, Location, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'short_text',
        'pub_date',
        'author',
        'location',
        'category',
        'is_published',
    )
    list_editable = (
        'is_published',
        'pub_date',
    )
    list_filter = (
        'category',
        'is_published'
    )
    search_fields = (
        'title',
    )
    list_select_related = (
        'author',
        'category',
        'location',
    )
    empty_value_display = 'Планета Земля'

    def short_text(self, obj):
        return obj.text[:MAX_LEN_TEXT] + '...'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'description',
        'slug',
        'is_published'
    )
    list_editable = (
        'is_published',
    )


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Comment._meta.get_fields()]
