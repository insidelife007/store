# Generated by Django 4.1.2 on 2023-08-08 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0010_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='pic',
            field=models.ImageField(default='profile.jpg', upload_to='Profile'),
        ),
    ]
