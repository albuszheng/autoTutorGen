# Generated by Django 2.0.3 on 2018-04-24 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('converter', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='behaviorgraph',
            name='trace',
            field=models.TextField(default=None),
        ),
    ]
