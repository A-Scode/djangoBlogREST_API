from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('test' , views.test),
    path('signup', views.signup),
    path('verifyotp' , views.otp_validation),
    path('loginmanully' , views.login_validation),
    path('forgototp' , views.send_forgot_opt)

]+static( settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
