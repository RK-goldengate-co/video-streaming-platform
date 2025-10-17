# CDN and Adaptive Bitrate Streaming Service
import subprocess
import os
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response

class AdaptiveBitrateService:
    """Service for handling adaptive bitrate streaming (HLS/DASH)"""
    
    # Quality presets for adaptive streaming
    QUALITY_PRESETS = [
        {'name': '1080p', 'width': 1920, 'height': 1080, 'bitrate': '5000k', 'audio_bitrate': '192k'},
        {'name': '720p', 'width': 1280, 'height': 720, 'bitrate': '2800k', 'audio_bitrate': '128k'},
        {'name': '480p', 'width': 854, 'height': 480, 'bitrate': '1400k', 'audio_bitrate': '128k'},
        {'name': '360p', 'width': 640, 'height': 360, 'bitrate': '800k', 'audio_bitrate': '96k'},
        {'name': '240p', 'width': 426, 'height': 240, 'bitrate': '400k', 'audio_bitrate': '64k'},
    ]
    
    @staticmethod
    def transcode_to_hls(input_file, output_dir):
        """Transcode video to HLS format with multiple quality levels"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Master playlist path
        master_playlist = os.path.join(output_dir, 'master.m3u8')
        
        # Build FFmpeg command for HLS with multiple variants
        ffmpeg_cmd = [
            'ffmpeg',
            '-i', input_file,
            '-filter_complex',
            ('[0:v]split=5[v1][v2][v3][v4][v5];'
             '[v1]scale=w=1920:h=1080[v1out];'
             '[v2]scale=w=1280:h=720[v2out];'
             '[v3]scale=w=854:h=480[v3out];'
             '[v4]scale=w=640:h=360[v4out];'
             '[v5]scale=w=426:h=240[v5out]'),
        ]
        
        # Add output streams for each quality
        for i, preset in enumerate(AdaptiveBitrateService.QUALITY_PRESETS, 1):
            variant_name = preset['name']
            output_path = os.path.join(output_dir, f'{variant_name}.m3u8')
            
            ffmpeg_cmd.extend([
                '-map', f'[v{i}out]',
                '-c:v:' + str(i-1), 'libx264',
                '-b:v:' + str(i-1), preset['bitrate'],
                '-maxrate:' + str(i-1), preset['bitrate'],
                '-bufsize:' + str(i-1), str(int(preset['bitrate'][:-1]) * 2) + 'k',
                '-map', 'a:0',
                '-c:a:' + str(i-1), 'aac',
                '-b:a:' + str(i-1), preset['audio_bitrate'],
            ])
        
        # Add HLS options
        ffmpeg_cmd.extend([
            '-f', 'hls',
            '-hls_time', '6',
            '-hls_playlist_type', 'vod',
            '-hls_segment_filename', os.path.join(output_dir, 'segment_%v_%03d.ts'),
            '-master_pl_name', 'master.m3u8',
            '-var_stream_map', ' '.join([f'v:{i},a:{i},name:{preset["name"]}' 
                                         for i, preset in enumerate(AdaptiveBitrateService.QUALITY_PRESETS)]),
            os.path.join(output_dir, '%v.m3u8')
        ])
        
        # Execute FFmpeg command
        try:
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, check=True)
            return {'success': True, 'master_playlist': master_playlist}
        except subprocess.CalledProcessError as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def transcode_to_dash(input_file, output_dir):
        """Transcode video to DASH format with multiple quality levels"""
        os.makedirs(output_dir, exist_ok=True)
        
        manifest_path = os.path.join(output_dir, 'manifest.mpd')
        
        # FFmpeg command for DASH
        ffmpeg_cmd = [
            'ffmpeg',
            '-i', input_file,
            '-map', '0:v',
            '-map', '0:a',
        ]
        
        # Add video streams with different bitrates
        for i, preset in enumerate(AdaptiveBitrateService.QUALITY_PRESETS):
            ffmpeg_cmd.extend([
                f'-s:v:{i}', f'{preset["width"]}x{preset["height"]}',
                f'-b:v:{i}', preset['bitrate'],
                f'-c:v:{i}', 'libx264',
            ])
        
        # Add audio encoding
        ffmpeg_cmd.extend([
            '-c:a', 'aac',
            '-b:a', '128k',
        ])
        
        # DASH-specific options
        ffmpeg_cmd.extend([
            '-f', 'dash',
            '-seg_duration', '6',
            '-use_template', '1',
            '-use_timeline', '1',
            '-init_seg_name', 'init_$RepresentationID$.m4s',
            '-media_seg_name', 'chunk_$RepresentationID$_$Number%05d$.m4s',
            manifest_path
        ])
        
        # Execute FFmpeg command
        try:
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, check=True)
            return {'success': True, 'manifest': manifest_path}
        except subprocess.CalledProcessError as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def generate_thumbnails(input_file, output_dir, interval=10):
        """Generate thumbnail sprites for video scrubbing"""
        os.makedirs(output_dir, exist_ok=True)
        
        # FFmpeg command to generate thumbnails
        ffmpeg_cmd = [
            'ffmpeg',
            '-i', input_file,
            '-vf', f'fps=1/{interval},scale=160:90',
            '-q:v', '5',
            os.path.join(output_dir, 'thumb_%04d.jpg')
        ]
        
        try:
            subprocess.run(ffmpeg_cmd, capture_output=True, text=True, check=True)
            return {'success': True, 'thumbnail_dir': output_dir}
        except subprocess.CalledProcessError as e:
            return {'success': False, 'error': str(e)}

class CDNService:
    """Service for CDN integration and caching"""
    
    # CDN providers configuration
    CDN_PROVIDERS = {
        'cloudflare': {
            'base_url': os.getenv('CLOUDFLARE_CDN_URL'),
            'zone_id': os.getenv('CLOUDFLARE_ZONE_ID'),
            'api_token': os.getenv('CLOUDFLARE_API_TOKEN')
        },
        'cloudfront': {
            'base_url': os.getenv('CLOUDFRONT_CDN_URL'),
            'distribution_id': os.getenv('CLOUDFRONT_DISTRIBUTION_ID')
        },
        'fastly': {
            'base_url': os.getenv('FASTLY_CDN_URL'),
            'service_id': os.getenv('FASTLY_SERVICE_ID'),
            'api_key': os.getenv('FASTLY_API_KEY')
        }
    }
    
    @staticmethod
    def get_cdn_url(file_path, provider='cloudflare'):
        """Generate CDN URL for a given file"""
        cdn_config = CDNService.CDN_PROVIDERS.get(provider)
        
        if not cdn_config or not cdn_config['base_url']:
            # Fallback to local serving if CDN not configured
            return f"{settings.MEDIA_URL}{file_path}"
        
        return f"{cdn_config['base_url']}/{file_path}"
    
    @staticmethod
    def purge_cache(file_paths, provider='cloudflare'):
        """Purge CDN cache for specific files"""
        cdn_config = CDNService.CDN_PROVIDERS.get(provider)
        
        if provider == 'cloudflare':
            import requests
            
            url = f"https://api.cloudflare.com/client/v4/zones/{cdn_config['zone_id']}/purge_cache"
            headers = {
                'Authorization': f"Bearer {cdn_config['api_token']}",
                'Content-Type': 'application/json'
            }
            data = {
                'files': [CDNService.get_cdn_url(path, provider) for path in file_paths]
            }
            
            response = requests.post(url, json=data, headers=headers)
            return response.json()
        
        return {'success': False, 'error': 'Unsupported CDN provider'}
    
    @staticmethod
    def set_cache_headers(response, max_age=3600):
        """Set appropriate cache headers for video content"""
        response['Cache-Control'] = f'public, max-age={max_age}'
        response['X-Content-Type-Options'] = 'nosniff'
        return response

# API Views
@api_view(['POST'])
def process_video_streaming(request):
    """Process video for adaptive streaming"""
    video_id = request.data.get('video_id')
    format_type = request.data.get('format', 'hls')  # hls or dash
    
    from ..models import Video
    
    try:
        video = Video.objects.get(id=video_id)
        input_file = video.file_path
        output_dir = os.path.join(settings.MEDIA_ROOT, 'streaming', str(video.id))
        
        if format_type == 'hls':
            result = AdaptiveBitrateService.transcode_to_hls(input_file, output_dir)
        elif format_type == 'dash':
            result = AdaptiveBitrateService.transcode_to_dash(input_file, output_dir)
        else:
            return Response({'error': 'Invalid format type'}, status=400)
        
        if result['success']:
            # Generate thumbnails
            thumb_dir = os.path.join(output_dir, 'thumbnails')
            AdaptiveBitrateService.generate_thumbnails(input_file, thumb_dir)
            
            # Update video with streaming URLs
            video.hls_url = CDNService.get_cdn_url(result.get('master_playlist', ''))
            video.dash_url = CDNService.get_cdn_url(result.get('manifest', ''))
            video.save()
            
            return Response({
                'message': 'Video processed successfully',
                'streaming_urls': {
                    'hls': video.hls_url,
                    'dash': video.dash_url
                }
            })
        else:
            return Response({'error': result.get('error')}, status=500)
    
    except Video.DoesNotExist:
        return Response({'error': 'Video not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
def purge_video_cache(request):
    """Purge CDN cache for a video"""
    video_id = request.data.get('video_id')
    provider = request.data.get('provider', 'cloudflare')
    
    from ..models import Video
    
    try:
        video = Video.objects.get(id=video_id)
        file_paths = [video.hls_url, video.dash_url]
        
        result = CDNService.purge_cache(file_paths, provider)
        return Response(result)
    
    except Video.DoesNotExist:
        return Response({'error': 'Video not found'}, status=404)
