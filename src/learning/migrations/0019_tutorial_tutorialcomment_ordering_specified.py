# Generated by Django 3.1.7 on 2021-04-14 11:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0018_tutorial_image_default_set_blank_false'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tutorial',
            options={'ordering': ('-create_date',), 'verbose_name': 'آموزش', 'verbose_name_plural': 'آموزش ها'},
        ),
        migrations.AlterModelOptions(
            name='tutorialcomment',
            options={'ordering': ('-create_date',), 'verbose_name': 'دیدگاه آموزش', 'verbose_name_plural': 'دیدگاه آموزش ها'},
        ),
    ]
