from .models import users , blogs, comments
from datetime import datetime
import json

def generate_user_id():
    no_of_users = len(users.objects.all())
    user_id = 'UID-'+ str(no_of_users+1)
    return user_id

def generate_blog_id():
    no_of_blogs = len(blogs.objects.all())
    blog_id = 'BID-'+str(no_of_blogs+1)
    return blog_id

def generate_comment_id():
    no_of_comments = len(comments.objects.all())
    comment_id = 'BID-'+str(no_of_comments+1)
    return comment_id

def serialize( modelObject ):
    modelDict = dict(modelObject)
    serialized_model = {}
    for key in modelDict:
        value = modelDict[key]
        value_type = type(value)
        
        if value_type == str:
            serialized_model[key] =  value
        elif value_type == int:
            serialized_model[key] = value
        elif value_type == datetime :
            serialized_model = value.strftime('%Y-%m-%d %T')
        else:
            raise TypeError('Unknown type to Serialize')
    return serialized_model

def write_users(dict):
    serialize(dict)
    file = open('users.json' , 'w')
    json.dump(dict , file , indent=4)
    file.flush()
    file.close()

def read_users():
    file = open('users.json' , 'r')
    object  = json.loads(file)
    return object

def add_one_blog(user_id):
    user = users.objects.get(user_id = user_id)
    user['blogs_upload'] += 1
    user.save(['blogs_upload'])
    