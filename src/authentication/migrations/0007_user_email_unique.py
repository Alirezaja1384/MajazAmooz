# Generated by Django 3.1.7 on 2021-05-03 15:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0006_user_scores_coins_integerfield"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(
                max_length=254, unique=True, verbose_name="ایمیل"
            ),
        ),
    ]
