from datetime import datetime
from functools import singledispatch
import mimetypes
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view,renderer_classes
from rest_framework.renderers import StaticHTMLRenderer
from .models import followings, users, blogs, comments,settings as users_settings,followers,signup_data,login_session
from . import utils
import json,os,shutil,base64
from django.conf import settings
from django.core.files.storage import FileSystemStorage


# Create your views here.

# import django.env_variables 
# django.env_variables.declare_variables()

@api_view(['GET'])
def test(request ):
    print(request.GET['hii'])
    return Response({"name" : 'shouryaraj'})


@api_view(['POST']) 
def signup(request):
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
            user.save()

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
            user_sign_up = signup_data(email = data['email']  , otp = otp_signup)
            user_sign_up.save()
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
    print(data['email'])
    signup_user = signup_data.objects.get(email = data['email'])
    user = users.objects.get(email= data['email'])
    if (data['otp'] == signup_user.otp):
        user_id = user.user_id
        user_settings = users_settings(user_id = user)
        user_settings.save()
        user_follower = followers(user_id = user)
        user_follower.save()
        user_following = followings(user_id = user)
        user_following.save()
        utils.ftp_upload_profile_photo(user_id)
        signup_data.objects.get(email = data['email']).delete()
        return Response({'staus': "success"})
    else:
        users.objects.filter(user_id = user.user_id ).delete()
        signup_data.objects.get(email = data['email']).delete()
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
    try:
        user = users.objects.get(email = data['email'])
        password = utils.decode_fernet(user.password)[:-6]
        if data['password'] == password:
            
            while True:
                try:
                    session = utils.create_session()
                    login_session.objects.filter(user_id = user.user_id).delete()
                    loggedin_user = login_session(user_id = user , session = session)
                    loggedin_user.save()
                    break
                except:continue
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
    try:
        login_data = login_session.objects.get(session = request.headers['session'])
        user_details = {"user_id": login_data.user_id.user_id}
    except:
        user_details={"user_id":"unknown"}
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
        user_list = utils.blogian_user_details(all_users)
        return Response({'status': 'success' , 'userslist': user_list} )
    except Exception as e:
        print(e)
        return Response({'status':'fail'})

@api_view(['POST'])
def logout_validation(request ):
    check_session = request.headers['session']
    user_id = request.headers['user_id']
    login_data = login_session.objects.get(session = check_session )
    if login_data.session == check_session:
        login_session.objects.filter(session = check_session ).delete()
        return Response({"status": "success"})
    else:
        return Response({'status' : 'fail'})


@api_view(['POST'])
def upload_blog(request):
    try:
        data = json.loads(request.POST['blogDetails'])
        check_session = request.headers['session']
        login_data = login_session.objects.get(session = check_session)
        if check_session == login_data.session:
            bid = utils.generate_blog_id()
            uid = login_data.user_id.user_id
            print(request.FILES)
            file_path = os.path.join(os.getcwd(), "uploaded_media" , uid , bid )
            if not os.path.exists(file_path):
                os.makedirs(file_path)
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
            utils.generate_blog(data['blog'],uid , bid ,file_path , )
            utils.blog_files_upload_to_ftp(uid , bid , file_path,data  )
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
        login_data = login_session.objects.get(session = check_session)
        if check_session == login_data.session:
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
        login_data = login_session.objects.get(session = check_session)
        if login_data.session == check_session:
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
    try:
        blogs_list = utils.blogs_details(blogs.objects.order_by('-views'))
        return Response({'status': 'success',"blogs_list":blogs_list})
    except:
        return Response({"status":"fail"})

@api_view(['GET'])
@renderer_classes([StaticHTMLRenderer])
def get_media(request):
    partial_url = request.GET['media']
    file_data,mime = utils.ftp_retrive_file(partial_url)
    return Response(file_data, content_type= mime)

@api_view(['POST'])
def get_followings_list(request):
    try:
        check_session = request.headers['session']
        login_data = login_session.objects.get(session = check_session)
        if check_session == login_data.session:
            follow_data = followings.objects.get(user_id = login_data.user_id.user_id)
            followings_list = json.loads(follow_data.followings)
            return Response({'status' : 'success'  , 'followings':followings_list})
        else:
            return Response({'status' : 'loginRequired'})
    except:
        return Response({'status':'fail'})

@api_view(['POST'])
def follow_unfollow(request):
    # try:
    check_sesssion = request.headers['session']
    state = request.headers['state']
    to_follow= request.headers['toFollow']
    login_data = login_session.objects.get(session = check_sesssion)
    if check_sesssion == login_data.session and to_follow != login_data.user_id.user_id:
        follow_data = followings.objects.get(user_id =login_data.user_id.user_id)
        followings_list = json.loads(follow_data.followings)
        followed_data = followers.objects.get(user_id = to_follow)
        followers_list = json.loads(followed_data.followers)
        print(state)
        if state == "Follow":
            followings_list.append(to_follow)
            followers_list.append(login_data.user_id.user_id)
            followings_list=list(set(followings_list))
            followers_list=list(set(followers_list))
            
        elif state == 'Following':
            followings_list.remove(to_follow)
            followers_list.remove(login_data.user_id.user_id)
            followings_list=list(set(followings_list))
            followers_list=list(set(followers_list))

        followings.objects.filter(user_id = login_data.user_id.user_id).update(followings = json.dumps(followings_list))
        followers.objects.filter(user_id = to_follow ).update(followers = json.dumps(followers_list))

        return Response({'status': 'success' , "followings":followings_list ,"followers_count":len(followers_list)})    
    else:
        return Response({'status' : 'loginRequired'})
    # except Exception as e:
    #     print(e)
    #     return Response({'status':'fail'})

@api_view(['POST'])
def get_user_details(request):
    user_id = request.headers['userId']
    data_to_send= {}
    profile_user = users.objects.get(user_id = user_id)
    data_to_send['userName']= profile_user.user_name
    data_to_send['email']=profile_user.email
    data_to_send['joinDatetime'] = profile_user.join_datetime.strftime('%a %d/%m/%Y')
    data_to_send['blogs']=utils.blogs_details(blogs.objects.filter(user_id = user_id).order_by('-upload_datetime'))
    data_to_send['comments']=utils.generate_comment_list(comments.objects.filter(user_id = user_id).order_by('-upload_datetime'))
    data_to_send['followings'] = utils.generate_follow_list(json.loads(followings.objects.get(user_id = user_id).followings))
    data_to_send['followers'] = utils.generate_follow_list(json.loads(followers.objects.get(user_id = user_id).followers))

    return Response({'status':'success' , "userData":data_to_send})
    