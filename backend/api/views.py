from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from rest_framework.authtoken.models import Token
import os
from django.core.files.storage import default_storage
from django.http import StreamingHttpResponse
import mimetypes

# User Authentication APIs
@api_view(['POST'])
def register_user(request):
    """
    Register a new user
    POST /api/register/
    {
        "username": "string",
        "email": "string",
        "password": "string"
    }
    """
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({'error': 'Username and password required'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.create_user(username=username, email=email, password=password)
    token, _ = Token.objects.get_or_create(user=user)
    
    return Response({
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'token': token.key
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def login_user(request):
    """
    Login user
    POST /api/login/
    {
        "username": "string",
        "password": "string"
    }
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    
    if user is not None:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'user_id': user.id,
            'username': user.username,
            'token': token.key
        })
    else:
        return Response({'error': 'Invalid credentials'}, 
                       status=status.HTTP_401_UNAUTHORIZED)


# Video Upload API
@api_view(['POST'])
def upload_video(request):
    """
    Upload video file
    POST /api/videos/upload/
    FormData: video file, title, description
    """
    if 'video' not in request.FILES:
        return Response({'error': 'No video file provided'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    video_file = request.FILES['video']
    title = request.data.get('title', 'Untitled')
    description = request.data.get('description', '')
    
    # Save video file
    file_path = default_storage.save(f'videos/{video_file.name}', video_file)
    
    # In production, save metadata to database
    video_data = {
        'id': 1,  # Would come from database
        'title': title,
        'description': description,
        'file_path': file_path,
        'uploaded_by': request.user.username if request.user.is_authenticated else 'anonymous'
    }
    
    return Response(video_data, status=status.HTTP_201_CREATED)


# Video Streaming API
@api_view(['GET'])
def stream_video(request, video_id):
    """
    Stream video
    GET /api/videos/{video_id}/stream/
    """
    # In production, fetch from database
    video_path = f'videos/sample_{video_id}.mp4'
    
    if not default_storage.exists(video_path):
        return Response({'error': 'Video not found'}, 
                       status=status.HTTP_404_NOT_FOUND)
    
    # Open video file
    video_file = default_storage.open(video_path, 'rb')
    content_type, _ = mimetypes.guess_type(video_path)
    
    # Create streaming response
    response = StreamingHttpResponse(
        video_file,
        content_type=content_type or 'video/mp4'
    )
    response['Content-Disposition'] = f'inline; filename="video_{video_id}.mp4"'
    
    return response


@api_view(['GET'])
def list_videos(request):
    """
    List all videos
    GET /api/videos/
    """
    # Mock data - in production, fetch from database
    videos = [
        {
            'id': 1,
            'title': 'Sample Video 1',
            'description': 'First sample video',
            'thumbnail': '/media/thumbnails/1.jpg',
            'duration': '5:30',
            'views': 1250
        },
        {
            'id': 2,
            'title': 'Sample Video 2',
            'description': 'Second sample video',
            'thumbnail': '/media/thumbnails/2.jpg',
            'duration': '8:45',
            'views': 890
        }
    ]
    
    return Response(videos)


# Comments API
@api_view(['GET', 'POST'])
def video_comments(request, video_id):
    """
    Get or post comments for a video
    GET /api/videos/{video_id}/comments/
    POST /api/videos/{video_id}/comments/
    {
        "text": "string"
    }
    """
    if request.method == 'GET':
        # Mock comments - in production, fetch from database
        comments = [
            {
                'id': 1,
                'user': 'user1',
                'text': 'Great video!',
                'timestamp': '2025-10-17T10:30:00Z'
            },
            {
                'id': 2,
                'user': 'user2',
                'text': 'Very informative, thanks!',
                'timestamp': '2025-10-17T11:15:00Z'
            }
        ]
        return Response(comments)
    
    elif request.method == 'POST':
        text = request.data.get('text')
        
        if not text:
            return Response({'error': 'Comment text required'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        # In production, save to database
        comment = {
            'id': 3,
            'user': request.user.username if request.user.is_authenticated else 'anonymous',
            'text': text,
            'timestamp': '2025-10-17T12:00:00Z'
        }
        
        return Response(comment, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
def delete_comment(request, comment_id):
    """
    Delete a comment
    DELETE /api/comments/{comment_id}/
    """
    # In production, delete from database with permission check
    return Response({'message': 'Comment deleted'}, status=status.HTTP_204_NO_CONTENT)
