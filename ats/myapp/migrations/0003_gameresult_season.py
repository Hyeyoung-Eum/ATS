# Generated by Django 5.0.6 on 2024-06-04 02:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='gameresult',
            name='season',
            field=models.IntegerField(default=1),
        ),
    ]