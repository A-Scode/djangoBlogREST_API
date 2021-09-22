from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('test' , views.test),
    path('signup', views.signup),
    path('verifyotp' , views.otp_validation),
    path('loginmanully' , views.login_validation),
    path('forgototp' , views.send_forgot_opt),
    path('validateforgototp' , views.validate_forgot_otp),
    path('changepassword' , views.change_password),
    path('getprofilephoto', views.get_profile_photo),
    path('userlist' , views.user_list),
    path('logout' , views.logout_validation),
    path('getSessionId' , views.get_session),
    path('uploadBlog',views.upload_blog),
    path('blogPreview' , views.getBlog_preview),
    path('getBlog' , views.getBlog)

]+static( settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
