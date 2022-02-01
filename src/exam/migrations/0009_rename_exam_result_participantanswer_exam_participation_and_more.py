# Generated by Django 4.0 on 2022-01-06 16:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0011_user_avatar_resize"),
        ("exam", "0008_auto_20220102_1315"),
    ]

    operations = [
        migrations.RenameModel("ExamResult", "ExamParticipation"),
        migrations.RenameField(
            model_name="participantanswer",
            old_name="exam_result",
            new_name="exam_participation",
        ),
        migrations.AlterField(
            model_name="examparticipation",
            name="questions",
            field=models.ManyToManyField(
                related_name="exam_participations",
                through="exam.ParticipantAnswer",
                to="exam.Question",
            ),
        ),
        migrations.AlterField(
            model_name="examparticipation",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="exam_participations",
                to="authentication.user",
                verbose_name="کاربر",
            ),
        ),
        migrations.AlterField(
            model_name="question",
            name="exam",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="questions",
                to="exam.exam",
            ),
        ),
    ]