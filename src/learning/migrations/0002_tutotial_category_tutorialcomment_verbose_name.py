# Generated by Django 3.1.7 on 2021-03-27 12:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name': 'دسته بندی ها'},
        ),
        migrations.AlterModelOptions(
            name='tutorial',
            options={'verbose_name': 'آموزش ها'},
        ),
        migrations.AlterModelOptions(
            name='tutorialcomment',
            options={'verbose_name': 'دیدگاه آموزش ها'},
        ),
    ]
