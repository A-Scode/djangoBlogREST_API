# Generated by Django 3.2.7 on 2021-09-23 16:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend_blog_tube', '0010_blogs_reviewers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogs',
            name='reviewers',
            field=models.JSONField(default='{}'),
        ),
    ]