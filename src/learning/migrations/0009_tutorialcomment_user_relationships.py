# Generated by Django 3.1.7 on 2021-03-28 11:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('learning', '0008_tutorial_comment_likes_upvotes_downvotes_name_changed'),
    ]

    operations = [
        migrations.CreateModel(
            name='TutorialCommentUpVote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.PositiveIntegerField(verbose_name='امتیاز')),
                ('coin', models.PositiveIntegerField(verbose_name='سکه')),
                ('TutorialComment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='learning.tutorialcomment', verbose_name='نظر آموزش')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='کاربر')),
            ],
        ),
        migrations.CreateModel(
            name='TutorialCommentLike',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.PositiveIntegerField(verbose_name='امتیاز')),
                ('coin', models.PositiveIntegerField(verbose_name='سکه')),
                ('TutorialComment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='learning.tutorialcomment', verbose_name='نظر آموزش')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='کاربر')),
            ],
        ),
        migrations.CreateModel(
            name='TutorialCommentDownVote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.PositiveIntegerField(verbose_name='امتیاز')),
                ('coin', models.PositiveIntegerField(verbose_name='سکه')),
                ('TutorialComment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='learning.tutorialcomment', verbose_name='نظر آموزش')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='کاربر')),
            ],
        ),
        migrations.AddField(
            model_name='tutorialcomment',
            name='down_votes',
            field=models.ManyToManyField(related_name='tutorial_comment_down_votes', through='learning.TutorialCommentDownVote', to=settings.AUTH_USER_MODEL, verbose_name='امتیاز منفی دیدگاه ها'),
        ),
        migrations.AddField(
            model_name='tutorialcomment',
            name='likes',
            field=models.ManyToManyField(related_name='tutorial_comment_likes', through='learning.TutorialCommentLike', to=settings.AUTH_USER_MODEL, verbose_name='لایک دیدگاه ها'),
        ),
        migrations.AddField(
            model_name='tutorialcomment',
            name='up_votes',
            field=models.ManyToManyField(related_name='tutorial_comment_up_votes', through='learning.TutorialCommentUpVote', to=settings.AUTH_USER_MODEL, verbose_name='امتیاز مثبت دیدگاه ها'),
        ),
    ]