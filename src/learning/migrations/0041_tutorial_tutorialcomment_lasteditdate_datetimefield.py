# Generated by Django 3.2.4 on 2021-06-20 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0040_score_coin_models_createdate_datetimefield_autonowadd_True'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutorial',
            name='last_edit_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='زمان آخرین ویرایش'),
        ),
        migrations.AlterField(
            model_name='tutorialcomment',
            name='last_edit_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='زمان آخرین ویرایش'),
        ),
    ]
