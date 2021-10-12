from django.contrib import admin
from .models import users , blogs , comments,settings, followers ,followings,login_session , signup_data

# Register your models here.
admin.site.register(users)
admin.site.register(blogs)
admin.site.register(comments)
admin.site.register(settings)
admin.site.register(followers)
admin.site.register(followings)
admin.site.register(login_session)
admin.site.register(signup_data)
