# Generated by Django 3.1.7 on 2021-04-20 19:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0023_tutorial_category_title_name_slug_unique_True_slug_blank_True'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutorial',
            name='confirm_status',
            field=models.IntegerField(choices=[(0, 'در انتظار تایید'), (1, 'تایید شده'), (-1, 'رد شده')], default=0, verbose_name='وضعیت تایید'),
        ),
        migrations.AlterField(
            model_name='tutorialcomment',
            name='confirm_status',
            field=models.IntegerField(choices=[(0, 'در انتظار تایید'), (1, 'تایید شده'), (-1, 'رد شده')], default=0, verbose_name='وضعیت تایید'),
        ),
    ]
