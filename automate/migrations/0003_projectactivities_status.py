# Generated by Django 4.1.4 on 2023-01-13 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("automate", "0002_projectactivities"),
    ]

    operations = [
        migrations.AddField(
            model_name="projectactivities",
            name="status",
            field=models.BooleanField(default=False),
        ),
    ]
