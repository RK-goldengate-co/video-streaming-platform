# Authentication Views
from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .oauth import SocialAuthService
import jwt
import os

# User Registration View
@api_view(['POST'])
def register_user(request):
    """Register a new user"""
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.create_user(username=username, email=email, password=password)
    token, _ = Token.objects.get_or_create(user=user)
    
    return Response({
        'token': token.key,
        'user_id': user.id,
        'username': user.username,
        'email': user.email
    }, status=status.HTTP_201_CREATED)

# User Login View
@api_view(['POST'])
def login_user(request):
    """Authenticate and login user"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    
    if user is not None:
        login(request, user)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username,
            'email': user.email
        })
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

# User Logout View
@api_view(['POST'])
def logout_user(request):
    """Logout user and delete token"""
    if request.user.is_authenticated:
        request.user.auth_token.delete()
        logout(request)
        return Response({'message': 'Successfully logged out'})
    return Response({'error': 'User not authenticated'}, status=status.HTTP_400_BAD_REQUEST)

# Social Login - Google
@api_view(['GET'])
def google_login(request):
    """Initiate Google OAuth flow"""
    google = SocialAuthService.get_provider('google')
    redirect_uri = request.build_absolute_uri('/api/auth/google/callback')
    return google.authorize_redirect(request, redirect_uri)

@api_view(['GET'])
def google_callback(request):
    """Handle Google OAuth callback"""
    google = SocialAuthService.get_provider('google')
    token = google.authorize_access_token(request)
    user_info = token.get('userinfo')
    
    # Get or create user
    user, created = User.objects.get_or_create(
        email=user_info['email'],
        defaults={'username': user_info['email'].split('@')[0]}
    )
    
    auth_token, _ = Token.objects.get_or_create(user=user)
    
    return Response({
        'token': auth_token.key,
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'is_new_user': created
    })

# Social Login - Facebook
@api_view(['GET'])
def facebook_login(request):
    """Initiate Facebook OAuth flow"""
    facebook = SocialAuthService.get_provider('facebook')
    redirect_uri = request.build_absolute_uri('/api/auth/facebook/callback')
    return facebook.authorize_redirect(request, redirect_uri)

@api_view(['GET'])
def facebook_callback(request):
    """Handle Facebook OAuth callback"""
    facebook = SocialAuthService.get_provider('facebook')
    token = facebook.authorize_access_token(request)
    user_info = facebook.get('me?fields=id,name,email').json()
    
    # Get or create user
    user, created = User.objects.get_or_create(
        email=user_info.get('email', f"{user_info['id']}@facebook.com"),
        defaults={'username': user_info.get('name', user_info['id'])}
    )
    
    auth_token, _ = Token.objects.get_or_create(user=user)
    
    return Response({
        'token': auth_token.key,
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'is_new_user': created
    })
