from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import users, blogs, comments
from . import utils
import json


# Create your views here.

@api_view(['GET'])
def test(request ):
    print(request.GET['hii'])
    return Response({"name" : 'shouryaraj'})


@api_view(['POST']) 
def signup(request):
    data = request['POST']





