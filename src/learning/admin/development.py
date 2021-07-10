"""
    Development learning models admin settings
"""
from django.contrib import admin

from learning.models import Category, Tutorial, TutorialTag, TutorialComment
from . import base


admin.site.register(Category, base.CategoryAdmin)
admin.site.register(Tutorial, base.TutorialAdmin)
admin.site.register(TutorialTag, base.TutorialTagAdmin)
admin.site.register(TutorialComment, base.TutorialCommentAdmin)
