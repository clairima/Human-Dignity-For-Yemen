from django.http import HttpResponseRedirect
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken
from api.serialize import RegisterSerializer, MyTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, redirect
from django.contrib.auth import logout as django_logout
from api.models import User
from django.contrib.auth import login as auth_login
from django.contrib import messages

@api_view(['POST'])
def register_view(request):
    if request.method == 'POST':
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            serializer = MyTokenObtainPairSerializer()
            tokens = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            return Response(tokens, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    return MyTokenObtainPairView.as_view()(request)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_view(request):
    user = request.user
    response_data = {
        'user_id': user.id,
        'username': user.username,
        'full_name': user.profile.full_name,
        'image': str(user.profile.image),
        'message': 'Dashboard data retrieved successfully',
    }
    return Response(response_data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    django_logout(request)
    return HttpResponseRedirect(redirect_to='home')

def logout(request):
    django_logout(request)
    return redirect('home')

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        # Retrieve data from the request
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        # Check if username is already taken
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return redirect('register')

        # Check if email is already taken
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return redirect('register')

        # Create the user
        user = User.objects.create_user(username=username, email=email, password=password1)

        # Log in the user
        auth_login(request, user)

        return redirect('dashboard')

    return render(request, 'register.html')

def login(request):
    return render(request, 'login.html')

def dashboard(request):
    return render(request, 'dashboard.html')