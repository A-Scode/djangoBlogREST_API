# Generated by Django 3.2.7 on 2021-09-26 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend_blog_tube', '0013_comments_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comments',
            name='comment',
            field=models.CharField(max_length=1000),
        ),
    ]