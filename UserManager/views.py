from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets
from UserManager.serializer import *
from django.contrib.auth import authenticate, login


class WorkbenchUserViewset(viewsets.ModelViewSet):
    queryset = WorkbenchUser.objects.all()
    serializer_class = WorkbenchUserSerializer


class UserViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


# Create your views here.
def index(request):
    return HttpResponse("Hello, world!")


def sign_in(request):
    if 'username' in request.POST and 'password' in request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return JsonResponse({"login": True})
    return JsonResponse({"login": False})