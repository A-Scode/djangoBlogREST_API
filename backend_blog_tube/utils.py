from .models import users , blogs, comments,followers
from datetime import datetime
import json,shutil,random,string
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
            serialized_model[key] = value.strftime('%Y-%m-%d %T')
        elif value_type == bool:
            serialized_model[key] = str(value).lower()
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
    new_width = 160
    new_height = int(new_width/ratio)
    resized_img = img.resize((new_width, new_height))
    resized_img.convert('RGB')
    resized_img.save(os.path.join(folder_path, "profile.jpg") )
    # img.save(os.path.join(folder_path,'profileLarge.jpg'))

def generate_otp():
    otp = str(random.randrange(1000,10000))
    return otp

def send_otp(otp ,username , email , type = "signup"):
    if type == 'signup':subject = 'OTP for Signup'
    else: subject = 'OTP for reset password'
    recipient_list = [email]
    email_from = settings.EMAIL_HOST_USER
    if  type == 'signup':html_msg = os.environ['email_template'].format(username , otp ,os.environ['logo'])
    else : html_msg = os.environ['forgot_password_template'].format(username , otp ,os.environ['logo'])
    send_mail(subject , "" , email_from, recipient_list ,html_message= html_msg )

def create_session():
    session_id = "".join(random.choices( string.ascii_letters , k  = 30))
    return session_id

def get_profile_photo_path(user_id):
    path = os.path.join(settings.MEDIA_ROOT ,user_id, 'profile' , 'profile.jpg' )
    unknown_user = os.path.join(settings.MEDIA_ROOT ,"assets","username.svg")

    if os.path.exists(path):
        return path
    else:
        return unknown_user

def check_is_follower(is_follower , of):
    check_with = json.loads(followers.objects.get(user_id = of).followers)
    if is_follower in check_with:
        return True
    else :
        return False

def generate_salt():
        salt = ''.join(random.choices(string.punctuation , k = 6))
        return salt