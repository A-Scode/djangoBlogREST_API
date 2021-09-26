# Generated by Django 3.2.3 on 2021-06-18 11:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='blogs',
            fields=[
                ('blog_id', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('blog_title', models.CharField(max_length=100)),
                ('upload_datetime', models.DateTimeField(auto_now_add=True)),
                ('likes', models.IntegerField(default=0)),
                ('dislikes', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='users',
            fields=[
                ('user_id', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('user_name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=100)),
                ('password', models.CharField(max_length=200)),
                ('join_datetime', models.DateTimeField(auto_now_add=True)),
                ('blogs_upload', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='comments',
            fields=[
                ('comment_id', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('upload_datetime', models.DateTimeField(auto_now_add=True)),
                ('blog_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend_blog_tube.blogs')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend_blog_tube.users')),
            ],
        ),
        migrations.AddField(
            model_name='blogs',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend_blog_tube.users'),
        ),
    ]