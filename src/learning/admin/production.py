"""
    Production learning models admin settings
"""
from django.contrib import admin
from django.contrib.admin.decorators import register

from learning.models import (
    Category, Tutorial,
    TutorialTag, TutorialComment
)


@register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """ Category admin settings """

    list_display = ('name', 'slug', 'parent_category', 'is_active',)

    readonly_fields = ('slug',)

    list_filter = ('is_active',)

    search_fields = ('name', 'slug',)


@register(Tutorial)
class TutorialAdmin(admin.ModelAdmin):
    """ Tutorial admin settings """

    def get_categories(self, obj: Tutorial) -> str:
        """
        @rtype: str
        @param obj: Tutorial object
        @return: category names
        """
        categories = [cat.name for cat in obj.categories.filter(is_active=True).only('name')]
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

    readonly_fields = ('slug', 'is_edited', 'author', 'title', 'slug',
                       'short_description', 'body', 'image',)

    def has_add_permission(self, request):
        return False


@register(TutorialTag)
class TutorialTagAdmin(admin.ModelAdmin):
    """ Tutorial admin settings """
    search_fields = ('title',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@register(TutorialComment)
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

    readonly_fields = ('user', 'tutorial', 'parent_comment',
                       'title', 'body',)

    def has_add_permission(self, request):
        return False
