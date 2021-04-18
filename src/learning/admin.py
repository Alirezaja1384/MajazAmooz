""" Learning models admin settings """
from django.contrib import admin
from django.conf import settings
from django.contrib.admin.decorators import register

from .models import (
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

    list_display = ('title', 'slug', 'user_views_count',
                    'likes_count', 'create_date', 'last_edit_date',
                    'confirm_status', 'is_active', 'is_edited', 'get_categories')

    list_filter = ('create_date', 'last_edit_date',
                   'confirm_status', 'is_active',)

    search_fields = ('title', 'short_description')

    fields = ('author', 'title', 'slug', 'short_description',
              'body', 'image', 'confirm_status', 'categories',
              'is_active', 'is_edited',)

    readonly_fields = ['slug', 'is_edited']

    def get_readonly_fields(self, request, obj=None):
        if not settings.DEBUG:
            self.readonly_fields += ['author', 'title', 'slug',
                                     'short_description', 'body', 'image']
        return self.readonly_fields

    def has_add_permission(self, request):
        return settings.DEBUG


@register(TutorialTag)
class TutorialTagAdmin(admin.ModelAdmin):
    """ Tutorial admin settings """
    search_fields = ('title',)

    def has_add_permission(self, request):
        return settings.DEBUG

    def has_change_permission(self, request, obj=None):
        return settings.DEBUG


@register(TutorialComment)
class TutorialCommentAdmin(admin.ModelAdmin):
    """ TutorialComment admin settings """
    list_display = ('title', 'parent_comment', 'create_date', 'last_edit_date', 'confirm_status',
                    'is_edited', 'allow_reply', 'notify_replies', 'is_active')

    fields = ['user', 'tutorial', 'parent_comment',
              'title', 'body', 'confirm_status', 'allow_reply',
              'notify_replies', 'is_active']

    list_filter = ('create_date', 'last_edit_date', 'confirm_status',
                   'is_edited', 'allow_reply', 'notify_replies', 'is_active',)

    search_fields = ('title', 'body',)

    readonly_fields = []

    def get_readonly_fields(self, request, obj=None):
        if not settings.DEBUG:
            self.readonly_fields += ['user', 'tutorial', 'parent_comment',
                                     'title', 'body']
        return self.readonly_fields

    def has_add_permission(self, request):
        return settings.DEBUG
