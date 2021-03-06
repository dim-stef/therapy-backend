# Generated by Django 3.1.4 on 2021-01-03 00:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('therapist', '0016_auto_20201228_0039'),
    ]

    operations = [
        migrations.AddField(
            model_name='therapist',
            name='afm',
            field=models.CharField(blank=True, max_length=60, null=True),
        ),
        migrations.AddField(
            model_name='therapist',
            name='doy',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AddField(
            model_name='therapist',
            name='iban',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AddField(
            model_name='therapist',
            name='id_back',
            field=models.ImageField(blank=True, null=True, upload_to='id/'),
        ),
        migrations.AddField(
            model_name='therapist',
            name='id_front',
            field=models.ImageField(blank=True, null=True, upload_to='id/'),
        ),
    ]
