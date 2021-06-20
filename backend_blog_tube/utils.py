from .models import users , blogs, comments
from datetime import datetime
import json,shutil,random
from cryptography.fernet import Fernet
from PIL  import Image
from django.conf import settings
from django.core.mail import send_mail

from django.env_variables import *
declare_variables()

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

def write_blogs(dict):
    serialize(dict)
    file = open('blogs.json' , 'w')
    json.dump(dict , file , indent=4)
    file.flush()
    file.close()

def read_blogs():
    file = open('blogs.json' , 'r')
    object  = json.loads(file)
    file.close()
    return object

def add_one_blog(user_id):
    user = users.objects.get(user_id = user_id)
    user['blogs_upload'] += 1
    user.save(['blogs_upload'])

def encode_fernet(en_str):
    fernet = Fernet(os.environ['fernet_key'])
    encode = fernet.encrypt(en_str.encode()).decode()
    return encode

def decode_fernet(de_str):
    fernet  = Fernet(os.environ['fernet_key'])
    decode  = fernet.decrypt(de_str.encode())
    return decode.decode()

def delete_user(uid):
    user = users.objects.get(user_id = uid)
    user.delete()
    path = os.path.join(os.getcwd(), "uploaded_media" , uid )
    if os.path.exists(path):
        shutil.rmtree(path)

def check_email(email):
    try:
        users.objects.get(email = email)
        return False
    except Exception as e:
        print(e)
        return True

def image_resize(folder_path , img_name):
    img = Image.open(os.path.join(folder_path , img_name))
    width , height = img.size
    ratio = width/height
    new_width = 80
    new_height = int(new_width/ratio)
    img = img.resize((new_width, new_height))
    img.convert('RGB')
    img.save(os.path.join(folder_path, "profile.jpg") )

def generate_otp():
    otp = str(random.randrange(1000,10000))
    return otp

def send_otp(otp ,username , email):
    subject = 'OTP for Signup'
    recipient_list = [email]
    email_from = settings.EMAIL_HOST_USER
    html_msg = os.environ['email_template'].format(username , otp )
    send_mail(subject , "" , email_from, recipient_list ,html_message= html_msg )

