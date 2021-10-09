
import urllib
from .models import users , blogs, comments,followers,settings as user_settings
from datetime import datetime
import json,shutil,random,string,os
from cryptography.fernet import Fernet
from PIL  import Image, ImageFilter ,ImageDraw , ImageFont
from django.conf import settings
from django.core.mail import send_mail
from urllib import request,error


import textwrap, mimetypes,ftplib

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
    img.save(os.path.join(folder_path , 'profileLarge.jpg'))
    img.close()
    resized_img.close()
    os.remove(os.path.join(folder_path , img_name))

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
    unknown_user = os.path.join(settings.MEDIA_ROOT ,"assets","username.svg")
    try:
        photo = urllib.request.urlopen(f'ftp://{os.environ["ftp_username"]}:{os.environ["ftp_pass"]}@{os.environ["ftp_provider"]}/htdocs/BlogTube/{user_id}/profile.jpg')
        return photo , photo.info().get_content_type()
    except Exception as e:
        photo = open(unknown_user , 'rb')
        return photo , 'image/svg+xml'

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
            if not preview: elem = (f"""<img className='blog_img' src ='{os.environ['current_url']}/backend_api/getMedia?media={uid}/{bid}/{part['name']}' 
            style='    border-radius: 5px;
    width: 90%;
    justify-self: center;
    object-fit: contain;
    box-shadow: rgb(0 0 0 / 20%) 0px 0px 5px 3px;
    aspect-ratio: 16 / 9;
    max-width: 500px;' loading="lazy" />""")
            else : elem = (f"""<img className='blog_img' src ='https://www.harborsidecrossfit.com/wp-content/uploads/revslider/home-demo/sample-image-white.png' 
            style='    border-radius: 5px;
    width: 90%;
    justify-self: center;
    object-fit: contain;
    box-shadow: rgb(0 0 0 / 20%) 0px 0px 5px 3px;
    aspect-ratio: 16 / 9;
    max-width: 500px;'  />""")
        elif keys[0]== "Video":
            if not preview :elem = (f"""<video preload controls className='blog_video' src ='{os.environ['current_url']}/backend_api/getMedia?media={uid}/{bid}/{part['name']}' style="    border-radius: 5px;
    width: 90%;
    justify-self: center;
    object-fit: contain;
    box-shadow: rgb(0 0 0 / 20%) 0px 0px 5px 3px;
    aspect-ratio: 16 / 9;
    max-width: 500px;" loading="lazy" />""")
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
    if not os.path.exists(file_path ):
            os.mkdir(file_path)
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
        back_img = back_img.resize((500 , 281))
        back_img.save(os.path.join(file_path,name)[:-3]+"png")
        img.close()
        back_img.close()
        os.remove(os.path.join(file_path , name))
    else :
        img = request.urlretrieve("https://picsum.photos/500/281",os.path.join(file_path , "title.png"))
        img = Image.open(os.path.join(file_path , "title.png"))
        img = img.filter(ImageFilter.GaussianBlur(3))
        t1 = ImageDraw.Draw(img)
        font = ImageFont.truetype('Prompt-BlackItalic.ttf' ,40)
        # font.set_variation_by_name('Italic')
        title = textwrap.fill(title ,width=14)
        t1.text((img.width//2,img.height//2) ,title , fill=(255,255,255) , font = font,anchor="mm" ,spacing=5 ,align='center')
        if not os.path.exists(file_path ):
            os.mkdir(file_path)
        img.save(os.path.join(file_path, name))
        img.close()
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
        data['blog_id'] = comment.blog_id.blog_id
        data['blog_title'] = comment.blog_id.blog_title
        comment_list.append(data)
    return comment_list

def getFileType(filepath):
    mime = mimetypes.guess_type(filepath)[0]
    return mime.split('/')[0]

def compress_img(filepath):
    aspect_ratio = 16/9
    img = Image.open(filepath)
    img_w ,img_h =  img.size
    img_ratio = img_w/img_h
    if img_ratio < aspect_ratio:
        new_img_h = 225
        new_img_w = (225*img_w)/img_h
    elif img_ratio > aspect_ratio:
        new_img_w = 400
        new_img_h = (400*img_h)/img_w
    else: 
        new_img_w = 400
        new_img_h = 225

    img = img.resize((int(new_img_w) , int(new_img_h)))
    img.save(filepath)

def ftpopen(path='/'):
    ftp = ftplib.FTP(os.environ['ftp_provider'])
    ftp.encoding = 'utf-8'
    ftp.login(os.environ['ftp_username'] , os.environ['ftp_pass'])
    if path != '/':ftp.cwd(path)
    return ftp
def ftpclose(ftp):
    ftp.close()

def ftp_del(path):
    ftp = ftpopen()
    ftp.delete(path)
    ftpclose(ftp)

def ftp_retrive_file(path):
    path = path.split('/')
    filename = path.pop()
    init_path = '/'.join(path)

    file_data = b''
    mime=''
    try:
        num = 1
        while True:
            file = request.urlopen(
            f"ftp://{os.environ['ftp_username']}:{os.environ['ftp_pass']}@{os.environ['ftp_provider']}/htdocs/BlogTube/{init_path}/__part{num}__{filename}"
                )
            file_data+= file.read()
            mime = file.info().get_content_type()
            file.close()
            num+= 1
    except error.URLError :
        return file_data ,mime

def blog_files_upload_to_ftp(uid,bid , filepath):
    ftp = ftpopen(f'/htdocs/BlogTube/{uid}')
    ftp.mkd(bid)
    ftp.cwd(bid)
    files = os.walk(filepath)
    files = next(files)[-1]
    files.remove(f'blog_{bid}.json')
    file2 = open(os.path.join(os.getcwd(),'compFile.bin') , 'wb+')
    for filename in files:
        file = open(os.path.join(filepath,filename) , 'rb')
        num = 1
        while True:
            data = file.read(10485760)
            if data != b'':
                file2.write(data)
                file2.flush()
                file2.seek(0)
                ftp.storbinary(f'STOR __part{num}__{filename}',file2)
                file2.seek(0)
                file2.write(b'')
            else:break
            num+=1
        file.close()
        os.remove(os.path.join(filepath,filename))

    file2.close()
    os.remove(os.path.join(os.getcwd(),'compFile.bin'))
    ftpclose(ftp)

def ftp_upload_profile_photo(uid):
    ftp = ftpopen('/htdocs/BlogTube')
    ftp.mkd(uid)
    ftp.cwd(uid)
    profile_path = os.path.join(settings.MEDIA_ROOT , uid , 'profile','profile.jpg')
    large_path = os.path.join(settings.MEDIA_ROOT , uid , 'profile','profileLarge.jpg')
    if os.path.exists( profile_path ):
        profile_photo  = open(profile_path , 'rb')
        large_photo  = open(large_path , 'rb')
        ftp.storbinary('STOR profile.jpg' , profile_photo)
        ftp.storbinary('STOR profile.jpg' , large_photo)
        profile_photo.close()
        large_photo.close()
    ftpclose(ftp)
    os.remove(profile_path)
    os.remove(large_path)
def blogs_details(all_blogs):
    blogs_list = []
    for blog in all_blogs:
        user = users.objects.get(user_id = blog.user_id.user_id)
        data = {}
        data['user_details']={'user_id': user.user_id,
                                'username': user.user_name}
        data['blog_details']={'blog_id': blog.blog_id,
                                'views':blog.views,
                                'likes': blog.likes,
                                'dislikes':blog.dislikes,
                                'title':blog.blog_title,
                                'discription':blog.discription,
                                'datetime':blog.upload_datetime.strftime("%a %d/%m/%Y %T"),
                                'blog_title_image':f"{os.environ['current_url']}/backend_api/getMedia?media={user.user_id}/{blog.blog_id}/title.png"
        }
        blogs_list.append(data)
    return blogs_list

def blogian_user_details(all_users):
    user_list = []
    for user in all_users:
        user_details = {}
        user_details['user_id'] = user.user_id
        user_details['user_name'] = user.user_name
        user_details['total_blogs'] = user.blogs_upload
        user_details['followers_count'] = len(json.loads(followers.objects.get(user_id  = user.user_id).followers))
        user_list.append(user_details)
    return user_list

def generate_follow_list(user_id_list):
    ret_list = []
    for i in user_id_list:
        user= users.objects.get(user_id = i)
        ret_list.append(user)
    ret_list = blogian_user_details(ret_list)
    return ret_list
    
    
                                

