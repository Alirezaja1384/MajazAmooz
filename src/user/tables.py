import django_tables2 as tables
from learning.models import Tutorial, TutorialComment


ACTION_TEMPLATE = '''
    {% if details_url %}
        <a href="{% url details_url record.pk %}" class="btn btn-sm btn-info">اطلاعات</a>
    {% endif %}

    {% if update_url %}
        <a href="{% url update_url record.pk %}" class="btn btn-sm btn-warning">ویرایش</a>
    {% endif %}

    {% if delete_url %}
        <a href="{% url delete_url record.pk %}" class="btn btn-sm btn-danger">حذف</a>
    {% endif %}
'''


class TutorialTable(tables.Table):

    actions = tables.TemplateColumn(
        ACTION_TEMPLATE, orderable=False,
        verbose_name='اقدام', extra_context={
            'details_url': 'user:tutorial_details',
            'update_url': 'user:tutorial_update',
            'delete_url': 'user:tutorial_delete',
        })

    class Meta:
        model = Tutorial
        fields = ('title', 'slug', 'user_views_count', 'likes_count',
                  'create_date', 'confirm_status', 'is_edited', 'is_active',)


class TutorialUserRelationsTable(tables.Table):
    _tutorial_link_template = '<a href="{% url \'learning:tutorial\' record.tutorial.slug %}">\
                               {{record.tutorial.title}}</a>'

    tutorial = tables.TemplateColumn(_tutorial_link_template)
    user = tables.Column(verbose_name='کاربر')
    score = tables.Column(verbose_name='امتیاز')
    coin = tables.Column(verbose_name='سکه')
    create_date = tables.Column(verbose_name='زمان')

    class Meta:
        fields = ('tutorial', 'user', 'score', 'coin', 'create_date',)


class TutorialCommentTable(tables.Table):

    _tutorial_link_template = '<a href="{% url \'learning:tutorial\' record.tutorial.slug %}">\
                              {{record.tutorial.title}}</a>'

    _parent_comment_link_template = ('<a href="{% url \'learning:tutorial\' record.tutorial.slug %}'
                                     '#comment-{{record.parent_comment_id}}">'
                                     '{{record.parent_comment.title}}</a>')


    tutorial = tables.TemplateColumn(_tutorial_link_template)
    parent_comment = tables.TemplateColumn(_parent_comment_link_template)

    actions = tables.TemplateColumn(
        ACTION_TEMPLATE, orderable=False,
        verbose_name='اقدام', extra_context={
            'details_url': 'user:tutorial_comment_details',
            'update_url': 'user:tutorial_comment_update',
            # 'delete_url': 'user:tutorial_comment_delete',
        })

    class Meta:
        model = TutorialComment
        fields = ('title', 'tutorial', 'parent_comment', 'create_date', 'last_edit_date',
                  'up_votes_count', 'down_votes_count', 'likes_count', 'confirm_status',
                  'is_edited', 'allow_reply', 'notify_replies', 'is_active',)
