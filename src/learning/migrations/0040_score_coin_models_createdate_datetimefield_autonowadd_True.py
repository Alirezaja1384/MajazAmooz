# Generated by Django 3.2.4 on 2021-06-20 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0039_tutorial_image_resize'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutorialcommentdownvote',
            name='create_date',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='زمان ایجاد'),
        ),
        migrations.AlterField(
            model_name='tutorialcommentlike',
            name='create_date',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='زمان ایجاد'),
        ),
        migrations.AlterField(
            model_name='tutorialcommentupvote',
            name='create_date',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='زمان ایجاد'),
        ),
        migrations.AlterField(
            model_name='tutorialdownvote',
            name='create_date',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='زمان ایجاد'),
        ),
        migrations.AlterField(
            model_name='tutoriallike',
            name='create_date',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='زمان ایجاد'),
        ),
        migrations.AlterField(
            model_name='tutorialupvote',
            name='create_date',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='زمان ایجاد'),
        ),
        migrations.AlterField(
            model_name='tutorialview',
            name='create_date',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='زمان ایجاد'),
        ),
    ]