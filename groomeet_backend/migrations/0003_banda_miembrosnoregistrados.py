# Generated by Django 3.1.7 on 2021-03-26 10:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groomeet_backend', '0002_auto_20210320_1345'),
    ]

    operations = [
        migrations.AddField(
            model_name='banda',
            name='miembrosNoRegistrados',
            field=models.CharField(max_length=500, null=True),
        ),
    ]
