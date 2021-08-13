# Generated by Django 3.2.4 on 2021-07-24 19:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0041_tutorial_tutorialcomment_lasteditdate_datetimefield'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutorialcommentdownvote',
            name='coin',
            field=models.IntegerField(default=0, editable=False, verbose_name='سکه'),
        ),
        migrations.AlterField(
            model_name='tutorialcommentdownvote',
            name='score',
            field=models.IntegerField(default=0, editable=False, verbose_name='امتیاز'),
        ),
        migrations.AlterField(
            model_name='tutorialcommentlike',
            name='coin',
            field=models.IntegerField(default=0, editable=False, verbose_name='سکه'),
        ),
        migrations.AlterField(
            model_name='tutorialcommentlike',
            name='score',
            field=models.IntegerField(default=0, editable=False, verbose_name='امتیاز'),
        ),
        migrations.AlterField(
            model_name='tutorialcommentupvote',
            name='coin',
            field=models.IntegerField(default=0, editable=False, verbose_name='سکه'),
        ),
        migrations.AlterField(
            model_name='tutorialcommentupvote',
            name='score',
            field=models.IntegerField(default=0, editable=False, verbose_name='امتیاز'),
        ),
        migrations.AlterField(
            model_name='tutorialdownvote',
            name='coin',
            field=models.IntegerField(default=0, editable=False, verbose_name='سکه'),
        ),
        migrations.AlterField(
            model_name='tutorialdownvote',
            name='score',
            field=models.IntegerField(default=0, editable=False, verbose_name='امتیاز'),
        ),
        migrations.AlterField(
            model_name='tutoriallike',
            name='coin',
            field=models.IntegerField(default=0, editable=False, verbose_name='سکه'),
        ),
        migrations.AlterField(
            model_name='tutoriallike',
            name='score',
            field=models.IntegerField(default=0, editable=False, verbose_name='امتیاز'),
        ),
        migrations.AlterField(
            model_name='tutorialupvote',
            name='coin',
            field=models.IntegerField(default=0, editable=False, verbose_name='سکه'),
        ),
        migrations.AlterField(
            model_name='tutorialupvote',
            name='score',
            field=models.IntegerField(default=0, editable=False, verbose_name='امتیاز'),
        ),
        migrations.AlterField(
            model_name='tutorialview',
            name='coin',
            field=models.IntegerField(default=0, editable=False, verbose_name='سکه'),
        ),
        migrations.AlterField(
            model_name='tutorialview',
            name='score',
            field=models.IntegerField(default=0, editable=False, verbose_name='امتیاز'),
        ),
    ]
