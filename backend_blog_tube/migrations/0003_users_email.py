# Generated by Django 3.2.3 on 2021-06-18 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend_blog_tube', '0002_remove_users_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='users',
            name='email',
            field=models.EmailField(default=None, max_length=100),
        ),
    ]