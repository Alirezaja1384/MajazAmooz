# Generated by Django 3.2.3 on 2021-06-12 20:18

from django.db import migrations
import utilities.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0037_tutorial_tutorialcomment_bleachfield'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutorialcomment',
            name='body',
            field=utilities.models.fields.BleachField(max_length=500, verbose_name='بدنه'),
        ),
    ]
