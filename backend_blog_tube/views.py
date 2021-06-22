from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view,renderer_classes
from rest_framework.renderers import StaticHTMLRenderer
from .models import users, blogs, comments
from . import utils
import json,os
from django.conf import settings
from django.core.files.storage import FileSystemStorage


# Create your views here.

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
            user = users( 
                user_id = uid ,
            user_name = data['username'],
            email = data['email'],
            password = utils.encode_fernet(data['password'])
            )

            if len(request.FILES) != 0:
                image_path = os.path.join(os.getcwd(), "uploaded_media" , uid , 'profile')
                if not os.path.exists(image_path):
                    os.makedirs(image_path)
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
    try:
        data = request.headers
        if (data['otp'] == otp_signup):
            user.save()
            return Response({'staus': "success"})
        else:
            print('fail OTP')
            return Response({'status' : "fail"})
    except:
        return Response({'status' : "fail"})

@api_view(['POST'])
def login_validation(request):
    data = json.loads(request.headers['credentails'])
    
    try:
        user = users.objects.get(email = data['email'])
        password = utils.decode_fernet(user.password)
        if data['password'] == password:
            return Response( {'status': 'success' ,
            "login_data" : {
                "user_id": user.user_id,
                "username": user.user_name,
                "email" : user.email,
                "encryp_pass":user.password
            },
            "session":utils.create_session() } )
        else :
            return Response({"status" : "not_match"})
    except Exception as error:
        print(error)
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
        new_pass = request.headers['newpass']
        
        users.objects.filter(user_id = user_forgot.user_id).update(password = utils.encode_fernet(new_pass))
        
        return Response({'status': 'success'})
    except Exception as error:
        print(error)
        return Response({'status' : 'fail'})

@api_view(['GET'])
@renderer_classes([StaticHTMLRenderer])
def get_profile_photo(request):

    user_id = request.GET['user_id']
    path =  utils.get_profile_photo_path(user_id)
    print(path)
    img = open(path , 'rb')
    img_data = img.read()
    return Response(img_data ,content_type= "image/*" )