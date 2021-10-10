from django.db import models
import json , string , random

from django.db.models.fields import CharField
from django.db.models.fields.related import ForeignKey


def generate_salt():
        salt = ''.join(random.choices(string.punctuation , k = 6))
        return salt


# Create your models here.
class users(models.Model):
    ''' user_id , user_name , join_datetime(auto) , blogs_upload(default= 0)'''
    user_id = models.CharField(max_length= 10 , primary_key= True , null = False)
    user_name = models.CharField(max_length= 100 , null = False)
    email = models.EmailField(max_length= 100 , null = False, default = None,unique=True)
    password = models.CharField(max_length=200  , null = False)
    join_datetime  = models.DateTimeField(auto_now=True , null = False)
    blogs_upload = models.IntegerField(default = 0)
    salt = models.CharField( null = False ,  default = generate_salt,max_length=6)

    def __iter__(self):
        self.list = [('user_id', self.user_id) , 
        ('user_name' , self.user_name),
        ('email' , self.email),
        ('join_datetime', self.join_datetime),
        ('blogs_upload' , self.blogs_upload)]

        self.n = 0
        return self

    def __next__(self):
        if self.n < len(self.list):
            item = self.list[self.n]
            self.n += 1
            return item
        else:
            raise StopIteration

class blogs(models.Model):
    ''' blog_id , user_id , upload_datetime(auto) , likes(0) , dislike(0) '''
    blog_id = models.CharField(max_length=10 , primary_key= True )
    blog_title = models.CharField(max_length=100 , null = False )
    user_id = models.ForeignKey(to = users , on_delete= models.CASCADE)
    upload_datetime = models.DateTimeField( auto_now=True)
    discription = models.CharField(max_length=200 , null = True )
    likes = models.IntegerField(default = 0)
    dislikes = models.IntegerField(default = 0)
    views = models.IntegerField(default=0)
    reviewers = models.JSONField(default = json.dumps({}))

    def __iter__(self):
        self.list = [('blog_id', self.blog_id) , 
        ('blog_title' , self.blog_title),
        ('user_id' , self.user_id),
        ('upload_datetime', self.upload_datetime),
        ('likes' , self.likes),
        ('dislikes',self.dislikes)]

        self.n = 0
        return self

    def __next__(self):
        if self.n < len(self.list):
            item = self.list[self.n]
            self.n += 1
            return item
        else:
            raise StopIteration




class comments(models.Model):
    ''' comment_id , user_id , upload_id , upload_datetime , reply_to(user_id , null= True)  , blog_id'''
    comment_id = models.CharField(max_length=10 , primary_key= True)
    user_id = models.ForeignKey(to = users , on_delete=models.CASCADE)
    comment = models.CharField(max_length=1000 , null=False)
    upload_datetime = models.DateTimeField(auto_now=True)
    blog_id = models.ForeignKey(to = blogs, null = False , on_delete = models.CASCADE)

    def __iter__(self):
        self.list = [('comment_id', self.comment_id) , 
        ('user_id' , self.user_id),
        ('upload_datetime', self.upload_datetime),
        ('blog_id' , self.blog_id)]

        self.n = 0
        return self

    def __next__(self):
        if self.n < len(self.list):
            item = self.list[self.n]
            self.n += 1
            return item
        else:
            raise StopIteration

class settings(models.Model):
    anonymus_choices = [( True,"show to anonymus") , 
                         (  False,"doesn't show to anonymus")
                     ]
    follower_choices = [( True,"show to followers") , 
                         ( False,"doesn't show to followers")
                     ]

    user_id = models.ForeignKey(to = users , on_delete = models.CASCADE)
    photo_to_anonymus = models.BooleanField(choices= anonymus_choices , default= True)
    email_to_anonymus = models.BooleanField(choices= anonymus_choices , default= True)
    photo_to_follower = models.BooleanField(choices= follower_choices , default= True)
    email_to_follower = models.BooleanField(choices= follower_choices , default= True)

    def __iter__(self):
        self.list = [('user_id', self.user_id) , 
        ('photo_to_anonymus' , self.photo_to_anonymus),
        ('email_to_anonymus', self.email_to_anonymus),
        ('photo_to_follower' , self.photo_to_follower),
        ('email_to_follower' , self.email_to_follower)
        ]
        

        self.n = 0
        return self

    def __next__(self):
        if self.n < len(self.list):
            item = self.list[self.n]
            self.n += 1
            return item
        else:
            raise StopIteration


class followers(models.Model):
    user_id = models.ForeignKey(to = users , on_delete = models.CASCADE)
    followers = models.JSONField(default = json.dumps([]))

class followings(models.Model):
    user_id = models.ForeignKey(to=users , on_delete=models.CASCADE)
    followings = models.JSONField( default = json.dumps([]))

class signup_data(models.Model):
    email = models.EmailField(max_length= 100 , unique=True)
    otp = models.CharField(max_length= 4 )

class login_session(models.Model):
    user_id = ForeignKey(to = users)
    session = CharField(max_length= 200,unique=True )

