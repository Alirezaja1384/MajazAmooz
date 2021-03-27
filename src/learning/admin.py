""" Learning models admin settings """
from django.contrib import admin
from django.contrib.admin.decorators import register

from .models import Tutorial


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
