# Generated by Django 3.1.4 on 2020-12-17 01:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('therapist', '0005_auto_20201214_0957'),
    ]

    operations = [
        migrations.AddField(
            model_name='therapist',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='therapist_avatars'),
        ),
    ]