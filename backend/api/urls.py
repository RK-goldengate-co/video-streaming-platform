from django.urls import path
from . import views

urlpatterns = [
    # Authentication endpoints
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    
    # Video endpoints
    path('videos/', views.list_videos, name='list-videos'),
    path('videos/upload/', views.upload_video, name='upload-video'),
    path('videos/<int:video_id>/stream/', views.stream_video, name='stream-video'),
    
    # Comment endpoints
    path('videos/<int:video_id>/comments/', views.video_comments, name='video-comments'),
    path('comments/<int:comment_id>/', views.delete_comment, name='delete-comment'),
]
