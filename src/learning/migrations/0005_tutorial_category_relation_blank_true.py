# Generated by Django 3.1.7 on 2021-03-27 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0004_tutorial_confirm_status_default_zero_nullable_false'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutorial',
            name='categories',
            field=models.ManyToManyField(blank=True, related_name='tutorials', to='learning.Category', verbose_name='دسته بندی ها'),
        ),
        migrations.AlterField(
            model_name='tutorial',
            name='confirm_status',
            field=models.IntegerField(choices=[(0, 'در انتظار تایید'), (-1, 'عدم تایید'), (1, 'تایید شده')], default=0, verbose_name='وضعیت تایید'),
        ),
    ]
