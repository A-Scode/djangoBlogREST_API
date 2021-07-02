from django.contrib import admin
from .models import users , blogs , comments,settings, followers ,followings

# Register your models here.
admin.site.register(users)
admin.site.register(blogs)
admin.site.register(comments)
admin.site.register(settings)
admin.site.register(followers)
admin.site.register(followings)
