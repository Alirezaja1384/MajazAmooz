# Generated by Django 3.2.3 on 2021-05-18 08:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0033_confirm_disprove_tutorialcomment_permission'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tutorial',
            options={'ordering': ('-create_date',), 'permissions': (('confirm_disprove_tutorial', 'تایید/رد آموزش ها'),), 'verbose_name': 'آموزش', 'verbose_name_plural': 'آموزش ها'},
        ),
    ]
