# Generated by Django 3.2.12 on 2022-03-17 11:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="avatar",
            name="image",
            field=models.ImageField(upload_to="avatars"),
        ),
    ]
