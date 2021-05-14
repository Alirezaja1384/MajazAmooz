"""
    Production learning models admin settings
"""
from django.contrib import admin
from django.db.models import Prefetch

from learning.models import (Tutorial, Category)
from .actions import (confirm_action, disprove_action)


class CategoryAdmin(admin.ModelAdmin):
    """ Category admin settings """

    list_display = ('name', 'slug', 'parent_category', 'is_active',)

    readonly_fields = ('slug',)

    list_filter = ('is_active',)

    search_fields = ('name', 'slug',)

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related('parent_category')
        return qs


class TutorialAdmin(admin.ModelAdmin):
    """ Tutorial admin settings """

    def get_categories(self, obj: Tutorial) -> str:
        """ Returns category names

        Args:
            obj (Tutorial): Tutorial object

        Returns:
            str: Name of categories as a string
        """
        categories = [cat.name for cat in obj.categories.all()]
        return '، '.join(categories)
    get_categories.short_description = 'دسته بندی ها'

    def get_tags(self, obj: Tutorial) -> str:
        """ Returns tutorial tags

        Args:
            obj (Tutorial): Tutorial object

        Returns:
            str: tutorial tags as a string
        """
        tags = [tag.title for tag in obj.tags.all()]
        return '، '.join(tags)
    get_tags.short_description = 'کلمات کلیدی'

    list_display = ('title', 'slug', 'author', 'user_views_count',
                    'likes_count', 'create_date', 'last_edit_date',
                    'confirm_status', 'is_active', 'is_edited',
                    'get_categories', 'get_tags')

    list_filter = ('create_date', 'last_edit_date',
                   'confirm_status', 'is_active',)

    search_fields = ('title', 'short_description',)

    fields = ('author', 'title', 'slug', 'short_description',
              'body', 'image', 'confirm_status', 'categories',
              'is_active', 'is_edited')

    actions = (confirm_action, disprove_action,)

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related('author').prefetch_related(
            Prefetch('categories', queryset=Category.objects.active_categories()), 'tags'
        )
        return qs


class TutorialTagAdmin(admin.ModelAdmin):
    """ Tutorial admin settings """

    list_display = ('title', 'tutorial',)
    search_fields = ('title', 'tutorial',)


class TutorialCommentAdmin(admin.ModelAdmin):
    """ TutorialComment admin settings """

    list_display = ('title', 'parent_comment', 'tutorial', 'user', 'create_date', 'last_edit_date',
                    'confirm_status', 'is_edited', 'allow_reply', 'notify_replies', 'is_active',)

    fields = ('user', 'tutorial', 'parent_comment',
              'title', 'body', 'confirm_status', 'allow_reply',
              'notify_replies', 'is_active',)

    list_filter = ('create_date', 'last_edit_date', 'confirm_status',
                   'is_edited', 'allow_reply', 'notify_replies', 'is_active',)

    search_fields = ('title', 'body',)

    actions = (confirm_action, disprove_action,)

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related('parent_comment', 'tutorial', 'user')
        return qs
