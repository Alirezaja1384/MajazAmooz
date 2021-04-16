# Generated by Django 3.1.7 on 2021-04-16 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0021_tutorial_isedited_default_False'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=models.SlugField(allow_unicode=True, unique=True, verbose_name='اسلاگ'),
        ),
        migrations.AlterField(
            model_name='tutorial',
            name='slug',
            field=models.SlugField(allow_unicode=True, unique=True, verbose_name='اسلاگ'),
        ),
    ]