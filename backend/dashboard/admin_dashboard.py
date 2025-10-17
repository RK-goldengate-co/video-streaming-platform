# Admin Dashboard - Analytics and Statistics
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.contrib.auth.models import User

class DashboardAnalytics:
    """Service for generating admin dashboard analytics"""
    
    @staticmethod
    def get_overview_stats():
        """Get overall platform statistics"""
        from ..models import Video, VideoView, Subscription
        
        total_users = User.objects.count()
        total_videos = Video.objects.count()
        total_views = VideoView.objects.count()
        active_subscriptions = Subscription.objects.filter(status='active').count()
        
        # Calculate growth rates
        last_30_days = timezone.now() - timedelta(days=30)
        new_users_30d = User.objects.filter(date_joined__gte=last_30_days).count()
        new_videos_30d = Video.objects.filter(created_at__gte=last_30_days).count()
        
        return {
            'total_users': total_users,
            'total_videos': total_videos,
            'total_views': total_views,
            'active_subscriptions': active_subscriptions,
            'new_users_30d': new_users_30d,
            'new_videos_30d': new_videos_30d,
            'revenue_30d': DashboardAnalytics.calculate_revenue(30)
        }
    
    @staticmethod
    def get_video_statistics():
        """Get detailed video statistics"""
        from ..models import Video, VideoView
        
        # Top 10 most viewed videos
        top_videos = Video.objects.annotate(
            view_count=Count('views')
        ).order_by('-view_count')[:10]
        
        # Videos by category
        videos_by_category = Video.objects.values('category').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Average video duration
        avg_duration = Video.objects.aggregate(Avg('duration'))['duration__avg']
        
        # View trends (last 7 days)
        view_trends = []
        for i in range(7):
            date = timezone.now() - timedelta(days=i)
            views = VideoView.objects.filter(
                viewed_at__date=date.date()
            ).count()
            view_trends.append({'date': date.strftime('%Y-%m-%d'), 'views': views})
        
        return {
            'top_videos': list(top_videos.values('id', 'title', 'view_count')),
            'videos_by_category': list(videos_by_category),
            'avg_duration': avg_duration,
            'view_trends': view_trends
        }
    
    @staticmethod
    def get_user_statistics():
        """Get detailed user statistics"""
        from ..models import Subscription, VideoView
        
        # User registration trends (last 30 days)
        registration_trends = []
        for i in range(30):
            date = timezone.now() - timedelta(days=i)
            count = User.objects.filter(date_joined__date=date.date()).count()
            registration_trends.append({'date': date.strftime('%Y-%m-%d'), 'count': count})
        
        # Active users (watched video in last 7 days)
        last_7_days = timezone.now() - timedelta(days=7)
        active_users = VideoView.objects.filter(
            viewed_at__gte=last_7_days
        ).values('user').distinct().count()
        
        # Subscription distribution
        subscription_stats = Subscription.objects.values('plan_type').annotate(
            count=Count('id')
        )
        
        return {
            'registration_trends': registration_trends,
            'active_users_7d': active_users,
            'subscription_distribution': list(subscription_stats)
        }
    
    @staticmethod
    def calculate_revenue(days=30):
        """Calculate revenue for specified period"""
        from ..models import Payment
        
        start_date = timezone.now() - timedelta(days=days)
        revenue = Payment.objects.filter(
            status='completed',
            created_at__gte=start_date
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        return float(revenue)
    
    @staticmethod
    def get_engagement_metrics():
        """Get user engagement metrics"""
        from ..models import Video, VideoView, Comment
        
        # Average watch time
        avg_watch_time = VideoView.objects.aggregate(
            Avg('watch_duration')
        )['watch_duration__avg'] or 0
        
        # Comment activity
        total_comments = Comment.objects.count()
        comments_last_7d = Comment.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        # Video completion rate
        completed_views = VideoView.objects.filter(completed=True).count()
        total_views = VideoView.objects.count()
        completion_rate = (completed_views / total_views * 100) if total_views > 0 else 0
        
        return {
            'avg_watch_time': avg_watch_time,
            'total_comments': total_comments,
            'comments_last_7d': comments_last_7d,
            'completion_rate': round(completion_rate, 2)
        }

# API Views
@api_view(['GET'])
@permission_classes([IsAdminUser])
def dashboard_overview(request):
    """Get dashboard overview statistics"""
    stats = DashboardAnalytics.get_overview_stats()
    return Response(stats)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def video_statistics(request):
    """Get video statistics"""
    stats = DashboardAnalytics.get_video_statistics()
    return Response(stats)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def user_statistics(request):
    """Get user statistics"""
    stats = DashboardAnalytics.get_user_statistics()
    return Response(stats)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def engagement_metrics(request):
    """Get engagement metrics"""
    metrics = DashboardAnalytics.get_engagement_metrics()
    return Response(metrics)
