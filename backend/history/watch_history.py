# User Watch History Service
from django.db import models
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import timedelta

class WatchHistory:
    """Service for managing user watch history"""
    
    @staticmethod
    def record_view(user, video, watch_duration, completed=False):
        """Record a video view in user's history"""
        from ..models import VideoView
        
        # Check if view already exists for this session
        existing_view = VideoView.objects.filter(
            user=user,
            video=video,
            viewed_at__gte=timezone.now() - timedelta(hours=1)
        ).first()
        
        if existing_view:
            # Update existing view
            existing_view.watch_duration = max(existing_view.watch_duration, watch_duration)
            existing_view.completed = completed or existing_view.completed
            existing_view.last_position = watch_duration
            existing_view.save()
            return existing_view
        else:
            # Create new view record
            view = VideoView.objects.create(
                user=user,
                video=video,
                watch_duration=watch_duration,
                completed=completed,
                last_position=watch_duration,
                viewed_at=timezone.now()
            )
            return view
    
    @staticmethod
    def get_user_history(user, limit=50):
        """Get user's watch history"""
        from ..models import VideoView
        
        history = VideoView.objects.filter(
            user=user
        ).select_related('video').order_by('-viewed_at')[:limit]
        
        return history
    
    @staticmethod
    def get_continue_watching(user, limit=10):
        """Get videos user started but didn't finish"""
        from ..models import VideoView
        
        continue_watching = VideoView.objects.filter(
            user=user,
            completed=False,
            watch_duration__gt=0
        ).select_related('video').order_by('-viewed_at')[:limit]
        
        return continue_watching
    
    @staticmethod
    def get_recommended_based_on_history(user, limit=20):
        """Get video recommendations based on watch history"""
        from ..models import VideoView, Video
        from django.db.models import Count
        
        # Get user's most watched categories
        watched_categories = VideoView.objects.filter(
            user=user
        ).values_list('video__category', flat=True)
        
        # Get category frequency
        category_counts = {}
        for category in watched_categories:
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Get top 3 categories
        top_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        top_category_names = [cat[0] for cat in top_categories]
        
        # Get watched video IDs to exclude
        watched_ids = VideoView.objects.filter(user=user).values_list('video_id', flat=True)
        
        # Recommend videos from top categories that user hasn't watched
        recommendations = Video.objects.filter(
            category__in=top_category_names
        ).exclude(
            id__in=watched_ids
        ).order_by('-views', '-created_at')[:limit]
        
        return recommendations
    
    @staticmethod
    def clear_history(user):
        """Clear user's watch history"""
        from ..models import VideoView
        
        deleted_count = VideoView.objects.filter(user=user).delete()[0]
        return deleted_count
    
    @staticmethod
    def remove_from_history(user, video_id):
        """Remove specific video from history"""
        from ..models import VideoView
        
        deleted_count = VideoView.objects.filter(
            user=user,
            video_id=video_id
        ).delete()[0]
        return deleted_count

# API Views
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def record_video_view(request):
    """Record a video view"""
    video_id = request.data.get('video_id')
    watch_duration = request.data.get('watch_duration', 0)
    completed = request.data.get('completed', False)
    
    from ..models import Video
    
    try:
        video = Video.objects.get(id=video_id)
        view = WatchHistory.record_view(
            user=request.user,
            video=video,
            watch_duration=watch_duration,
            completed=completed
        )
        
        return Response({
            'message': 'View recorded successfully',
            'view_id': view.id
        })
    except Video.DoesNotExist:
        return Response({'error': 'Video not found'}, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_watch_history(request):
    """Get user's watch history"""
    limit = int(request.GET.get('limit', 50))
    history = WatchHistory.get_user_history(request.user, limit=limit)
    
    history_data = [{
        'id': item.id,
        'video_id': item.video.id,
        'video_title': item.video.title,
        'video_thumbnail': item.video.thumbnail_url,
        'watch_duration': item.watch_duration,
        'last_position': item.last_position,
        'completed': item.completed,
        'viewed_at': item.viewed_at.isoformat()
    } for item in history]
    
    return Response(history_data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_continue_watching(request):
    """Get videos to continue watching"""
    limit = int(request.GET.get('limit', 10))
    videos = WatchHistory.get_continue_watching(request.user, limit=limit)
    
    continue_data = [{
        'video_id': item.video.id,
        'video_title': item.video.title,
        'video_thumbnail': item.video.thumbnail_url,
        'last_position': item.last_position,
        'duration': item.video.duration,
        'progress_percentage': (item.last_position / item.video.duration * 100) if item.video.duration > 0 else 0
    } for item in videos]
    
    return Response(continue_data)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_watch_history(request):
    """Clear user's entire watch history"""
    deleted_count = WatchHistory.clear_history(request.user)
    return Response({'message': f'{deleted_count} items removed from history'})

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_history(request, video_id):
    """Remove specific video from history"""
    deleted_count = WatchHistory.remove_from_history(request.user, video_id)
    if deleted_count > 0:
        return Response({'message': 'Video removed from history'})
    else:
        return Response({'error': 'Video not found in history'}, status=404)
