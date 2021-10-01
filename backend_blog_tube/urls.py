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
    path('getBlog' , views.getBlog),
    path('checkReviewr',views.check_reviewer),
    path('Blogreview' , views.blog_review),
    path('uploadComment', views.upload_comment),
    path('getComments' , views.get_comments),
    path('retriveHomeBlogs' , views.retrive_home_blogs),
    path('getMedia', views.get_media),
    path('getFollowingList' , views.get_followings_list),
    path('followUnfollow' , views.follow_unfollow)

]+static( settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
