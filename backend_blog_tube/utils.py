from .models import users , blogs, comments,followers,settings as user_settings
from datetime import datetime
import json,shutil,random,string
from cryptography.fernet import Fernet
from PIL  import Image, ImageFilter ,ImageDraw , ImageFont
from django.conf import settings
from django.core.mail import send_mail
from urllib import request
import textwrap

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
    comment_id = 'CID-'+str(no_of_comments+1)
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

def generate_elem_list(data ,uid  , bid , preview = False):
    data_lsit = []

    for part in data:
        keys = list(part.keys())
        if keys[0] == "Heading":
            elem = f"""<h3 className = 'blog_heading' >{part[keys[0]]}</h3>"""
        elif keys[0] == "Paragraph":
            elem = f"""<p className = 'blog_para'>{part[keys[0]]}</p>"""
        elif keys[0] == "Photo":
            if not preview: elem = (f"""<img className='blog_img' src ='{os.environ['current_url']}/media/{uid}/{bid}/{part['name']}' 
            style='    border-radius: 5px;
    width: 90%;
    justify-self: center;
    object-fit: contain;
    box-shadow: rgb(0 0 0 / 20%) 0px 0px 5px 3px;
    aspect-ratio: 16 / 9;
    max-width: 500px;'  />""")
            else : elem = (f"""<img className='blog_img' src ='https://www.harborsidecrossfit.com/wp-content/uploads/revslider/home-demo/sample-image-white.png' 
            style='    border-radius: 5px;
    width: 90%;
    justify-self: center;
    object-fit: contain;
    box-shadow: rgb(0 0 0 / 20%) 0px 0px 5px 3px;
    aspect-ratio: 16 / 9;
    max-width: 500px;'  />""")
        elif keys[0]== "Video":
            if not preview :elem = (f"""<video controls className='blog_video' src ='{os.environ['current_url']}/media/{uid}/{bid}/{part['name']}' style="    border-radius: 5px;
    width: 90%;
    justify-self: center;
    object-fit: contain;
    box-shadow: rgb(0 0 0 / 20%) 0px 0px 5px 3px;
    aspect-ratio: 16 / 9;
    max-width: 500px;" />""")
            else:elem = (f"""<video controls className='blog_video' src ='http://techslides.com/demos/sample-videos/small.mp4' style="    border-radius: 5px;
    width: 90%;
    justify-self: center;
    object-fit: contain;
    box-shadow: rgb(0 0 0 / 20%) 0px 0px 5px 3px;
    aspect-ratio: 16 / 9;
    max-width: 500px;" />""")
        elif keys[0] == "Youtube Video":
            elem = (f'''<iframe src='https://www.youtube.com/embed/{part[keys[0]]}'
        title="YouTube video player" frameborder="0" style="border-radius: 5px;
    justify-self: center;
    box-shadow: rgb(0 0 0 / 20%) 0px 0px 5px 3px;
    aspect-ratio: 16 / 9;
    width: inherit;
    max-width: 500px;"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
        allowfullscreen></iframe>''')
        elif keys[0] =="List":
            elem = "<ul>"
            for i in part[keys[0]]:
                elem += f"<li>{i}</li>"
            elem += "</ul>"
        data_lsit.append(elem)
    return data_lsit


def generate_blog(data , uid  , bid ,file_path ,details):
    blog_elem_list = generate_elem_list(data ,uid,bid)
    file = open(os.path.join(file_path,f"blog_{bid}.json"),'w')
    file.write(json.dumps(blog_elem_list,indent= 4))
    file.close()
    user = users.objects.get(user_id = uid)
    blog = blogs(blog_id = bid ,user_id = user, blog_title = details['title'],discription = details['discription'])
    users.objects.filter(user_id = uid).update(blogs_upload= user.blogs_upload+1)
    blog.save()

def edit_title_image(name , file_path,empty = False,title=""):
    if not empty:
        img = Image.open(os.path.join(file_path,name))
        img_w , img_h = img.size
        back_img_h = (img_w*(9/16))
        back_img_box = (0,int((img_h-back_img_h)/2) ,img_w,int(((img_h-back_img_h)/2)+back_img_h))
        back_img = img.crop(back_img_box)
        back_img = back_img.resize((int(img_h*(16/9)), img_h))
        back_img = back_img.filter(ImageFilter.GaussianBlur(3))
        back_img.paste(img,( int((back_img.size[0]-img_w)/2),0))
        back_img.save(os.path.join(file_path,name)[:-3]+"png")
    else :
        img = request.urlretrieve("https://picsum.photos/1600/900",os.path.join(file_path , "title.png"))
        img = Image.open(os.path.join(file_path , "title.png"))
        img = img.filter(ImageFilter.GaussianBlur(3))
        t1 = ImageDraw.Draw(img)
        font = ImageFont.truetype('Prompt-BlackItalic.ttf' ,170)
        # font.set_variation_by_name('Italic')
        title = textwrap.fill(title ,width=14)
        t1.text((img.width//2,img.height//2) ,title , fill=(255,255,255) , font = font,anchor="mm" ,spacing=5 ,align='left')
        img.save(os.path.join(file_path, name))
def getUID(bid):
    data = blogs.objects.get(blog_id = bid)
    uid = data.user_id.user_id
    return uid

def returnSettings(uid):
    uid = str(uid)
    owner_settings = user_settings.objects.get(user_id = uid)
    return owner_settings

def generate_comment_list(query_set):
    comment_list = []
    for comment in query_set:
        data = {}
        data['cid'] = comment.comment_id
        data['uid']= comment.user_id.user_id
        data['name'] = comment.user_id.user_name
        data['text'] = comment.comment
        data['upload_datetime'] = comment.upload_datetime.strftime("%a %d/%m/%Y %T")
        comment_list.append(data)
    return comment_list