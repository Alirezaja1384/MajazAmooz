# Generated by Django 3.1.7 on 2021-03-30 12:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('learning', '0014_tutorial_comment_manytomany_rlationship_deleted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutorialcomment',
            name='tutorial',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='comments', to='learning.tutorial', verbose_name='آموزش'),
        ),
        migrations.AlterField(
            model_name='tutorialcomment',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tutorial_comments', to=settings.AUTH_USER_MODEL, verbose_name='کاربر'),
        ),
    ]
