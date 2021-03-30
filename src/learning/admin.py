""" Learning models admin settings """
from django.contrib import admin
from django.contrib.admin.decorators import register

from .models import (
    Category, Tutorial,
    TutorialTag, TutorialComment
)


@register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """ Category admin settings """

    list_display = ('name', 'slug', 'parent_category', 'is_active', )

    list_filter = ('is_active', )

    search_fields = ('name', 'slug', )

    prepopulated_fields = {"slug": ("name", )}


@register(Tutorial)
class TutorialAdmin(admin.ModelAdmin):
    """ Tutorial admin settings """

    list_display = ('title', 'slug', 'user_views_count',
                    'likes_count', 'create_date', 'last_edit_date',
                    'confirm_status', 'is_active',)

    list_filter = ('create_date', 'last_edit_date',
                   'confirm_status', 'is_active', )

    search_fields = ('title', 'short_description')

    fields = ('title', 'slug', 'short_description', 'body',
              'image', 'confirm_status', 'is_active', 'categories',)

    prepopulated_fields = {"slug": ("title", )}


@register(TutorialTag)
class TutorialTagAdmin(admin.ModelAdmin):
    """ Tutorial admin settings """
    search_fields = ('title', )


@register(TutorialComment)
class TutorialCommentAdmin(admin.ModelAdmin):
    """ TutorialComment admin settings """
    list_display = ('title', 'create_date', 'last_edit_date', 'confirm_status',
                    'is_edited', 'allow_reply', 'notify_replies', 'is_active')

    fields = ('title', 'body', 'confirm_status', 'is_edited',
              'allow_reply', 'notify_replies', 'is_active', 'user', 'tutorial', 'parent_comment',)

    list_filter = ('create_date', 'last_edit_date', 'confirm_status',
                   'is_edited', 'allow_reply', 'notify_replies', 'is_active',)

    search_fields = ('title', 'body', )
