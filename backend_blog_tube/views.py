from datetime import datetime
import mimetypes
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view,renderer_classes
from rest_framework.renderers import StaticHTMLRenderer
from .models import followings, users, blogs, comments,settings as users_settings,followers
from . import utils
import json,os,shutil,urllib.request
from django.conf import settings
from django.core.files.storage import FileSystemStorage


# Create your views here.

login_data = {}
session = ""


@api_view(['GET'])
def test(request ):
    print(request.GET['hii'])
    return Response({"name" : 'shouryaraj'})


@api_view(['POST']) 
def signup(request):
    global user ,otp_signup
    try:
        data = json.loads(request.headers['userData'])
        if utils.check_email(data['email']):
            uid = utils.generate_user_id()
            salt  = utils.generate_salt()
            user = users( 
                user_id = uid ,
            user_name = data['username'],
            email = data['email'],
            password = utils.encode_fernet(data['password']+salt),
            salt = salt
            )

            image_path = os.path.join(os.getcwd(), "uploaded_media" , uid , 'profile')
            if not os.path.exists(image_path):
                os.makedirs(image_path)
            if len(request.FILES) != 0:
                fs =  FileSystemStorage(image_path)
                file = request.FILES['image']
                file_name  = file.name
                file_url = fs.save(f'{uid}_profile'+file_name[ (len(file_name)-(file_name[::-1].find("."))-1):], file)
                print(file_url)
                utils.image_resize(image_path , file_url)

            otp_signup = utils.generate_otp()
            utils.send_otp(otp_signup , data['username'], data['email'])
            print("sucess")
            return Response({'status': "otp"})
        
        else:
            return Response({'status':'exists'})
    except Exception as error :
        print(error)
        return Response({'status' : "fail"})

@api_view(['POST'])
def otp_validation(request):
    # try:
    data = request.headers
    if (data['otp'] == otp_signup):
        user_id = user.user_id
        user.save()
        user.refresh_from_db()
        user_settings = users_settings(user_id = user)
        user_settings.save()
        user_follower = followers(user_id = user)
        user_follower.save()
        user_following = followings(user_id = user)
        user_following.save()
        utils.ftp_upload_profile_photo(user_id)
        return Response({'staus': "success"})
    else:
        print('fail OTP')
        image_path = os.path.join(os.getcwd(), "uploaded_media" , user.user_id )
        if os.path.exists(image_path):
            shutil.rmtree(os.path.join(settings.MEDIA_ROOT, user.user_id))
        return Response({'status' : "fail"})
    # except Exception as e:
    #     print(e)
    #     return Response({'status' : "fail"})

@api_view(['POST'])
def login_validation(request):
    data = json.loads(request.headers['credentails'])
    global login_data , session
    
    try:
        user = users.objects.get(email = data['email'])
        password = utils.decode_fernet(user.password)[:-6]
        if data['password'] == password:
            session = utils.create_session()
            login_data = {
                "user_id": user.user_id,
                "username": user.user_name,
                "email" : user.email,
                "encryp_pass":user.password
            }
            return Response( {'status': 'success' ,
            "login_data" : {
                "user_id": user.user_id,
                "username": user.user_name,
                "email" : user.email,
                "encryp_pass":user.password
            },
            "session":session } )
        else :
            return Response({"status" : "not_match"})
    except Exception as error:
        login_data = {}
        session = ""
        return Response({"status" : "fail"})

@api_view(['POST'])
def send_forgot_opt(request):
    try:
        global otp_forgot,user_forgot
        data = json.loads(request.headers['userdata'])
        email = data['email']


        if not utils.check_email(email):
            user_forgot = users.objects.get(email = data['email'])
            otp_forgot = utils.generate_otp()
            utils.send_otp(otp_forgot ,user_forgot.user_name , email , type = 'forgot_otp' )
            return Response({'status' : 'success'})
        else:
            return Response({'status': 'error'})
    except Exception as error:
        print(error)
        return Response({'status': 'error'})

@api_view(['POST'])
def validate_forgot_otp(request):
    try:
        otp = request.headers['otp']
        if otp == otp_forgot:
            return Response({'status' : 'success'})
        else:
            return Response({'status': 'fail'})
    except:
            return Response({'status': 'fail'})

@api_view(['POST'])
def change_password(request):
    try:
        salt = utils.generate_salt()

        new_pass = request.headers['newpass']+salt
        
        users.objects.filter(user_id = user_forgot.user_id).update(password = utils.encode_fernet(new_pass), salt = salt)
        
        return Response({'status': 'success'})
    except Exception as error:
        print(error)
        return Response({'status' : 'fail'})

@api_view(['POST'])
@renderer_classes([StaticHTMLRenderer])
def get_profile_photo(request):     #Must send user details for POST if unkown than userID unknown
    if request.headers['session'] == session and request.headers['session'] :
        user_details = login_data
    else: 
        user_details= {"user_id" : "unknown"}
    photo_uid = request.headers['photouid']
    if photo_uid != "undefined":
        owner_settings = utils.returnSettings(photo_uid)
        if utils.check_is_follower(user_details['user_id'], photo_uid):
            if owner_settings.photo_to_follower :
                user_id = photo_uid
            else:
                user_id = 'unknown'
        else:
            if owner_settings.photo_to_anonymus :
                user_id = photo_uid
            else : 
                user_id = "unknown"
    else : 
        user_id = "unknown"

    print(user_id)
    img ,type =  utils.get_profile_photo_path(user_id)
    img_data = img.read()
    img.close()
    return Response(img_data ,content_type= type )

@api_view(['GET'])
def user_list(request):
    try:
        all_users = users.objects.all()
        user_list = []
        for user in all_users:
            user_details = {}
            user_details['user_id'] = user.user_id
            user_details['user_name'] = user.user_name
            user_details['total_blogs'] = user.blogs_upload
            user_details['followers_count'] = len(json.loads(followers.objects.get(user_id  = user.user_id).followers))
            user_list.append(user_details)
        return Response({'status': 'success' , 'userslist': user_list} )
    except Exception as e:
        print(e)
        return Response({'status':'fail'})

@api_view(['POST'])
def logout_validation(request ):
    global session

    check_session = json.loads(request.headers['session'])
    if session == check_session:
        session = ""
        return Response({"status": "success"})
    else:
        return Response({'status' : 'fail'})

@api_view(['POST','GET'])
def get_session(request):
    return Response({'session': session})

@api_view(['POST'])
def upload_blog(request):
    try:
        data = json.loads(request.POST['blogDetails'])
        check_session = request.headers['session']
        if check_session == session:
            bid = utils.generate_blog_id()
            uid = login_data['user_id']
            print(request.FILES)
            file_path = os.path.join(os.getcwd(), "uploaded_media" , uid , bid )
            if not os.path.exists(file_path):
                os.mkdir(file_path)
            for name in request.FILES:
                fs = FileSystemStorage(file_path)
                file = request.FILES[name]
                print(utils.getFileType(file.name))
                if name == "blog_title_image":
                    name="title."+file.name[-3:]
                    if os.path.exists(os.path.join(file_path, name)):
                        os.remove(os.path.join(file_path, name))
                file_url = fs.save( name , file)
                file_type = utils.getFileType(os.path.join(settings.MEDIA_ROOT , uid ,bid,name))
                if name[:-3] == "title.":
                    utils.edit_title_image(name , file_path)
                elif file_type == 'image':
                    utils.compress_img(os.path.join(settings.MEDIA_ROOT , uid ,bid,name))
            if data['blog_title_image'] == "":
                utils.edit_title_image("title.png" , file_path , empty=True , title=data['title'])
            utils.generate_blog(data['blog'],uid , bid ,file_path ,data )
            utils.blog_files_upload_to_ftp(uid , bid , file_path)
        else:
            return Response({"status" :"loginRequired"})
        return Response({"status":"success"})
    except Exception as e:
        print(e)
        return Response({'status': 'fail'})

@api_view(['GET'])
def getBlog(request):
    try:
        bid = request.GET['blog_id']
        uid = utils.getUID(bid)
        blogger = users.objects.get(user_id = uid)
        user_details = {}
        user_details['user_id'] = blogger.user_id
        user_details['user_name'] = blogger.user_name
        user_details['total_blogs'] = blogger.blogs_upload
        user_details['followers_count'] = len(json.loads(followers.objects.get(user_id  = blogger.user_id).followers))
        file = open(os.path.join(settings.MEDIA_ROOT,uid ,bid ,f"blog_{bid}.json" ))
        data = json.load(file)
        file.close()
        blog = blogs.objects.get(blog_id  = bid)
        blogs.objects.filter(blog_id = bid ).update(views = blog.views +1 )
        return Response({"status":"success" , "blog": data ,"title": blog.blog_title ,
        "likes":blog.likes ,"dislikes":blog.dislikes , "views":blog.views ,"image_url": f"{os.environ['current_url']}/backend_api/getMedia?media={uid}/{bid}/title.png",
                    "blogger_details":user_details})
    except Exception as e:
        print(e)
        return Response({"status":"fail"})

@api_view(['POST'])
def getBlog_preview(request):
    try:
        blog = json.loads(request.POST['blog'])
        check_session = request.headers['session']
        if check_session == session:
            blog_elem_list = utils.generate_elem_list(blog , '' , '' , preview=True)
            return Response({"status": "success" , "hydratedBlog" : blog_elem_list })
        else : 
            return Response({"status" : "loginRequired"})
    except Exception as e:
        print(e)
        return Response({"status":"fail"})
@api_view(['GET'])
def check_reviewer(request):
    bid = request.GET['bid']
    uid = request.GET['uid']
    blog = blogs.objects.get(blog_id = bid)
    reviewers = json.loads(blog.reviewers)
    if uid in reviewers:
        return Response({'status' : 'success' , 'isreviewer':reviewers[uid]})
    else:
        return Response({'status' : 'success' , 'isreviewer':"not yet"})

@api_view(['POST'])
def blog_review(request):
    uid = request.POST['uid']
    bid = request.POST['bid']
    review = request.POST['review']
    print(review)
    blog = blogs.objects.get(blog_id = bid)
    reviewers = json.loads(blog.reviewers)
    if review == "like":
        if uid in reviewers and reviewers[uid]== "dislike":
            blogs.objects.filter(blog_id = bid).update(dislikes = blog.dislikes-1)
        if uid in reviewers and reviewers[uid]== "like":pass
        else:
            reviewers[uid]=review    
            blogs.objects.filter(blog_id = bid).update(reviewers=json.dumps(reviewers) ,likes = blog.likes+1)
            return Response({'status':'success' ,'details': {"likes" : blog.likes+1 ,
             "dislikes":blog.dislikes-1 , "views" : blog.views}})

    elif review == "dislike":
        if uid in reviewers and reviewers[uid]== "like":
            blogs.objects.filter(blog_id = bid).update(likes = blog.likes-1)
        if uid in reviewers and reviewers[uid]== "dislike":pass
        else:
            reviewers[uid]=review
            blogs.objects.filter(blog_id = bid).update(reviewers=json.dumps(reviewers) ,dislikes = blog.dislikes+1)
            return Response({'status':'success' ,
            'details': {"likes" : blog.likes-1 ,
             "dislikes":blog.dislikes+1 , "views" : blog.views}})


    return Response({'status':'success' ,
    'details': {"likes" : blog.likes , "dislikes":blog.dislikes ,
     "views" : blog.views}})

@api_view(['POST'])
def upload_comment(request):
    try:
        check_session = request.headers['session']
        if session == check_session:
            comment = request.POST['comment']
            c_user = users.objects.get(user_id = request.POST['user_id'])
            blog_id = blogs.objects.get(blog_id =request.POST['blog_id'])
            cid = utils.generate_comment_id()
            comment_model = comments(comment_id = cid , user_id = c_user , comment = comment, blog_id=blog_id )
            comment_model.save()
            return Response({"status":"success"  , "new_comment" : {"cid" :cid, "uid":c_user.user_id ,"name" :c_user.user_name, "text" :comment,"upload_datetime" :datetime.now().strftime("%a %d/%m/%Y %T")}})
        else:
            return Response({"status":"login_required"})
    except Exception as e:
        print(e)
        return Response({"status":"fail"})

@api_view(['POST'])
def get_comments(request):
    blog_id = request.POST['blog_id']
    comments_obj_list = comments.objects.filter(blog_id = blog_id).order_by('-upload_datetime')
    comment_list = utils.generate_comment_list(comments_obj_list)
    return Response({"status" :"success" , "comment_list" : comment_list})

@api_view(['POST'])
def retrive_home_blogs(request):
    blogs_list = utils.home_blogs()
    return Response({'status': 'success',"blogs_list":blogs_list})

@api_view(['GET'])
@renderer_classes([StaticHTMLRenderer])
def get_media(request):
    partial_url = request.GET['media']
    file_data,mime = utils.ftp_retrive_file(partial_url)
    return Response(file_data, content_type= mime)