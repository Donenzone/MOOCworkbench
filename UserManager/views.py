from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets
from UserManager.serializer import *
from django.contrib.auth import authenticate, login


# Create your views here.
class WorkbenchUserViewset(viewsets.ModelViewSet):
    queryset = WorkbenchUser.objects.all().order_by('-created')
    serializer_class = WorkbenchUserSerializer


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