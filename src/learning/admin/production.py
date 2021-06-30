"""
    Production learning models admin settings
"""
from django.contrib import admin
from django.contrib.admin.decorators import register

from learning.models import Category, Tutorial, TutorialTag, TutorialComment
from . import base


admin.site.register(Category, base.CategoryAdmin)


@register(Tutorial)
class TutorialAdmin(base.TutorialAdmin):
    """Tutorial admin settings"""

    readonly_fields = (
        "slug",
        "is_edited",
        "author",
        "title",
        "slug",
        "short_description",
        "body",
        "image",
    )

    def has_add_permission(self, request):
        return False


@register(TutorialTag)
class TutorialTagAdmin(base.TutorialTagAdmin):
    """Tutorial admin settings"""

    readonly_fields = ("tutorial",)

    def has_add_permission(self, request):
        return False


@register(TutorialComment)
class TutorialCommentAdmin(base.TutorialCommentAdmin):
    """TutorialComment admin settings"""

    readonly_fields = (
        "user",
        "tutorial",
        "parent_comment",
        "title",
        "body",
    )

    def has_add_permission(self, request):
        return False
