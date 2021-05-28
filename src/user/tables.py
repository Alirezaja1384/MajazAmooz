import django_tables2 as tables
from learning.models import Tutorial


ACTION_TEMPLATE = '''
    <a href="{% url details_url record.pk %}" class="btn btn-sm btn-info">اطلاعات</a>
    <a href="{% url update_url record.pk %}" class="btn btn-sm btn-warning">ویرایش</a>
'''


class TutorialTable(tables.Table):

    details = tables.TemplateColumn(
        ACTION_TEMPLATE, orderable=False,
        verbose_name='اقدام', extra_context={
            'details_url': 'user:tutorial_details',
            'update_url': 'user:tutorial_update',
        })

    class Meta:
        model = Tutorial
        template_name = "django_tables2/bootstrap4.html"
        fields = ('title', 'slug', 'user_views_count', 'likes_count',
                  'create_date', 'confirm_status', 'is_edited', 'is_active',)
