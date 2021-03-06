# Generated by Django 3.1.7 on 2021-05-03 09:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('learning', '0028_tutorialcomment_tutorialcommentrelations_relatedname'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tutorial',
            name='down_votes',
        ),
        migrations.RemoveField(
            model_name='tutorial',
            name='likes',
        ),
        migrations.RemoveField(
            model_name='tutorial',
            name='up_votes',
        ),
        migrations.RemoveField(
            model_name='tutorial',
            name='views',
        ),
        migrations.AddField(
            model_name='tutorial',
            name='down_voters',
            field=models.ManyToManyField(related_name='down_voted_tutorials', through='learning.TutorialDownVote', to=settings.AUTH_USER_MODEL, verbose_name='امتیاز های منفی'),
        ),
        migrations.AddField(
            model_name='tutorial',
            name='likers',
            field=models.ManyToManyField(related_name='liked_tutorials', through='learning.TutorialLike', to=settings.AUTH_USER_MODEL, verbose_name='لایک ها'),
        ),
        migrations.AddField(
            model_name='tutorial',
            name='up_voters',
            field=models.ManyToManyField(related_name='up_voted_tutorials', through='learning.TutorialUpVote', to=settings.AUTH_USER_MODEL, verbose_name='امتیاز های مثبت'),
        ),
        migrations.AddField(
            model_name='tutorial',
            name='viewers',
            field=models.ManyToManyField(related_name='viewed_tutorials', through='learning.TutorialView', to=settings.AUTH_USER_MODEL, verbose_name='بازدید ها'),
        ),
        migrations.AlterField(
            model_name='tutorialdownvote',
            name='tutorial',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='down_votes', to='learning.tutorial', verbose_name='آموزش'),
        ),
        migrations.AlterField(
            model_name='tutorialdownvote',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tutorial_down_votes', to=settings.AUTH_USER_MODEL, verbose_name='کاربر'),
        ),
        migrations.AlterField(
            model_name='tutoriallike',
            name='tutorial',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='learning.tutorial', verbose_name='آموزش'),
        ),
        migrations.AlterField(
            model_name='tutoriallike',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tutorial_likes', to=settings.AUTH_USER_MODEL, verbose_name='کاربر'),
        ),
        migrations.AlterField(
            model_name='tutorialupvote',
            name='tutorial',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='up_votes', to='learning.tutorial', verbose_name='آموزش'),
        ),
        migrations.AlterField(
            model_name='tutorialupvote',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tutorial_up_votes', to=settings.AUTH_USER_MODEL, verbose_name='کاربر'),
        ),
        migrations.AlterField(
            model_name='tutorialview',
            name='tutorial',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='views', to='learning.tutorial', verbose_name='آموزش'),
        ),
        migrations.AlterField(
            model_name='tutorialview',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tutorial_views', to=settings.AUTH_USER_MODEL, verbose_name='کاربر'),
        ),
    ]
