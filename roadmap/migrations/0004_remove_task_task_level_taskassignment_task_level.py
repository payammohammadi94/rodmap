# Generated by Django 5.1.7 on 2025-05-26 07:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roadmap', '0003_project_doing_step_project_task_task_level_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='task_level',
        ),
        migrations.AddField(
            model_name='taskassignment',
            name='task_level',
            field=models.IntegerField(choices=[(1, 'EASY'), (2, 'MEDIUM'), (3, 'HARD'), (4, 'CHALLENGE'), (5, 'SHORT TIME')], default=1),
        ),
    ]
