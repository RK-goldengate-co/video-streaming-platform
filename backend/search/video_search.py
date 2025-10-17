# Video Search and Filter Service
from django.db.models import Q, Count, Avg
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

class VideoSearchService:
    """Service for searching and filtering videos"""
    
    @staticmethod
    def search_videos(query, filters=None):
        """Search videos with optional filters"""
        from ..models import Video
        
        # Start with all videos
        queryset = Video.objects.all()
        
        # Apply text search if query provided
        if query:
            # Use Q objects for complex search across multiple fields
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(tags__icontains=query) |
                Q(category__icontains=query)
            )
        
        # Apply filters
        if filters:
            # Category filter
            if 'category' in filters and filters['category']:
                queryset = queryset.filter(category=filters['category'])
            
            # Duration range filter (in seconds)
            if 'min_duration' in filters:
                queryset = queryset.filter(duration__gte=filters['min_duration'])
            if 'max_duration' in filters:
                queryset = queryset.filter(duration__lte=filters['max_duration'])
            
            # Upload date filter
            if 'date_from' in filters:
                queryset = queryset.filter(created_at__gte=filters['date_from'])
            if 'date_to' in filters:
                queryset = queryset.filter(created_at__lte=filters['date_to'])
            
            # View count filter
            if 'min_views' in filters:
                queryset = queryset.filter(views__gte=filters['min_views'])
            
            # Quality filter
            if 'quality' in filters and filters['quality']:
                queryset = queryset.filter(quality=filters['quality'])
            
            # Status filter (published, draft, etc.)
            if 'status' in filters and filters['status']:
                queryset = queryset.filter(status=filters['status'])
        
        return queryset
    
    @staticmethod
    def sort_videos(queryset, sort_by='newest'):
        """Sort video queryset by specified criteria"""
        sort_options = {
            'newest': '-created_at',
            'oldest': 'created_at',
            'most_viewed': '-views',
            'least_viewed': 'views',
            'longest': '-duration',
            'shortest': 'duration',
            'title_asc': 'title',
            'title_desc': '-title'
        }
        
        order_by = sort_options.get(sort_by, '-created_at')
        return queryset.order_by(order_by)
    
    @staticmethod
    def get_popular_searches(limit=10):
        """Get most popular search queries"""
        from ..models import SearchLog
        
        popular = SearchLog.objects.values('query').annotate(
            count=Count('id')
        ).order_by('-count')[:limit]
        
        return [item['query'] for item in popular]
    
    @staticmethod
    def get_trending_videos(days=7, limit=20):
        """Get trending videos based on recent views"""
        from ..models import Video, VideoView
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        trending = Video.objects.filter(
            views__viewed_at__gte=cutoff_date
        ).annotate(
            recent_view_count=Count('views')
        ).order_by('-recent_view_count')[:limit]
        
        return trending
    
    @staticmethod
    def get_category_suggestions():
        """Get all available categories with video counts"""
        from ..models import Video
        
        categories = Video.objects.values('category').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return categories
    
    @staticmethod
    def advanced_search(params):
        """Advanced search with PostgreSQL full-text search"""
        from ..models import Video
        
        query_text = params.get('query', '')
        
        if not query_text:
            return Video.objects.none()
        
        # Create search vector
        search_vector = SearchVector('title', weight='A') + \
                       SearchVector('description', weight='B') + \
                       SearchVector('tags', weight='C')
        
        # Create search query
        search_query = SearchQuery(query_text)
        
        # Apply search and rank results
        results = Video.objects.annotate(
            search=search_vector,
            rank=SearchRank(search_vector, search_query)
        ).filter(search=search_query).order_by('-rank')
        
        return results
    
    @staticmethod
    def log_search(user, query, result_count):
        """Log search query for analytics"""
        from ..models import SearchLog
        
        SearchLog.objects.create(
            user=user if user.is_authenticated else None,
            query=query,
            result_count=result_count
        )

class VideoPagination(PageNumberPagination):
    """Custom pagination for video results"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

# API Views
@api_view(['GET'])
def search_videos(request):
    """Search and filter videos"""
    query = request.GET.get('q', '')
    
    # Build filters from query params
    filters = {
        'category': request.GET.get('category'),
        'min_duration': request.GET.get('min_duration'),
        'max_duration': request.GET.get('max_duration'),
        'date_from': request.GET.get('date_from'),
        'date_to': request.GET.get('date_to'),
        'min_views': request.GET.get('min_views'),
        'quality': request.GET.get('quality'),
        'status': request.GET.get('status', 'published')
    }
    
    # Remove None values
    filters = {k: v for k, v in filters.items() if v is not None}
    
    # Search videos
    videos = VideoSearchService.search_videos(query, filters)
    
    # Sort results
    sort_by = request.GET.get('sort', 'newest')
    videos = VideoSearchService.sort_videos(videos, sort_by)
    
    # Log search
    VideoSearchService.log_search(request.user, query, videos.count())
    
    # Paginate results
    paginator = VideoPagination()
    paginated_videos = paginator.paginate_queryset(videos, request)
    
    video_data = [{
        'id': video.id,
        'title': video.title,
        'description': video.description,
        'thumbnail': video.thumbnail_url,
        'duration': video.duration,
        'views': video.views,
        'category': video.category,
        'created_at': video.created_at.isoformat()
    } for video in paginated_videos]
    
    return paginator.get_paginated_response(video_data)

@api_view(['GET'])
def get_categories(request):
    """Get all available categories"""
    categories = VideoSearchService.get_category_suggestions()
    return Response(list(categories))

@api_view(['GET'])
def get_trending(request):
    """Get trending videos"""
    days = int(request.GET.get('days', 7))
    limit = int(request.GET.get('limit', 20))
    
    trending = VideoSearchService.get_trending_videos(days, limit)
    
    trending_data = [{
        'id': video.id,
        'title': video.title,
        'thumbnail': video.thumbnail_url,
        'views': video.recent_view_count,
        'category': video.category
    } for video in trending]
    
    return Response(trending_data)

@api_view(['GET'])
def popular_searches(request):
    """Get popular search queries"""
    limit = int(request.GET.get('limit', 10))
    searches = VideoSearchService.get_popular_searches(limit)
    return Response({'popular_searches': searches})
