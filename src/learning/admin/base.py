"""
    Production learning models admin settings
"""
from django.contrib import admin

from learning.models import Tutorial
from .actions import (confirm_action, disprove_action)


class CategoryAdmin(admin.ModelAdmin):
    """ Category admin settings """

    list_display = ('name', 'slug', 'parent_category', 'is_active',)

    readonly_fields = ('slug',)

    list_filter = ('is_active',)

    search_fields = ('name', 'slug',)


class TutorialAdmin(admin.ModelAdmin):
    """ Tutorial admin settings """

    def get_categories(self, obj: Tutorial) -> str:
        """ Returns category names

        Args:
            obj (Tutorial): Tutorial object

        Returns:
            str: Name of categories as a string
        """
        categories = [cat.name for cat in obj.categories.filter(
            is_active=True).only('name')]
        return '، '.join(categories)
    get_categories.short_description = 'دسته بندی ها'

    list_display = ('title', 'slug', 'author', 'user_views_count',
                    'likes_count', 'create_date', 'last_edit_date',
                    'confirm_status', 'is_active', 'is_edited', 'get_categories',)

    list_filter = ('create_date', 'last_edit_date',
                   'confirm_status', 'is_active',)

    search_fields = ('title', 'short_description',)

    fields = ('author', 'title', 'slug', 'short_description',
              'body', 'image', 'confirm_status', 'categories',
              'is_active', 'is_edited',)

    actions = (confirm_action, disprove_action,)


class TutorialTagAdmin(admin.ModelAdmin):
    """ Tutorial admin settings """

    list_display = ('title', 'tutorial',)
    search_fields = ('title', 'tutorial',)


class TutorialCommentAdmin(admin.ModelAdmin):
    """ TutorialComment admin settings """

    list_display = ('title', 'parent_comment', 'tutorial', 'create_date', 'last_edit_date',
                    'confirm_status', 'is_edited', 'allow_reply', 'notify_replies', 'is_active',)

    fields = ('user', 'tutorial', 'parent_comment',
              'title', 'body', 'confirm_status', 'allow_reply',
              'notify_replies', 'is_active',)

    list_filter = ('create_date', 'last_edit_date', 'confirm_status',
                   'is_edited', 'allow_reply', 'notify_replies', 'is_active',)

    search_fields = ('title', 'body',)

    actions = (confirm_action, disprove_action,)
