import django_tables2 as table

from learning.models import Tutorial


class TutorialTable(table.Table):
    class Meta:
        model = Tutorial
        template_name = "django_tables2/bootstrap4.html"
        fields = ('title', 'slug', 'user_views_count', 'likes_count',
                  'create_date', 'confirm_status', 'is_edited', 'is_active',)
