# Generated by Django 3.1.4 on 2021-01-04 00:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('therapist', '0017_auto_20210103_0015'),
    ]

    operations = [
        migrations.CreateModel(
            name='TherapistSpecialties',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('specialty', models.CharField(max_length=50)),
                ('therapist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='specialties', to='therapist.therapist')),
            ],
        ),
    ]
