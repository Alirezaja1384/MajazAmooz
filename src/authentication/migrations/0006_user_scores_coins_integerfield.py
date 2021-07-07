# Generated by Django 3.1.7 on 2021-05-02 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0005_user_avatar_default_set_blank_false"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="coins",
            field=models.IntegerField(default=0, verbose_name="سکه ها"),
        ),
        migrations.AlterField(
            model_name="user",
            name="scores",
            field=models.IntegerField(default=0, verbose_name="امتیاز"),
        ),
    ]
