# Generated by Django 3.2.12 on 2022-03-17 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('problems', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='problemmedia',
            name='media_type',
        ),
        migrations.RemoveField(
            model_name='problemmedia',
            name='problem',
        ),
        migrations.RemoveField(
            model_name='problemmedia',
            name='public_id',
        ),
        migrations.AddField(
            model_name='problemmedia',
            name='image',
            field=models.ImageField(default='abcd', upload_to='ProblemMedia'),
            preserve_default=False,
        ),
    ]
