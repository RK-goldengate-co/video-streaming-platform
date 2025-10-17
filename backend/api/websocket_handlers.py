import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer

class CommentConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time comments
    Usage: ws://localhost:8000/ws/comments/{video_id}/
    """
    
    async def connect(self):
        self.video_id = self.scope['url_route']['kwargs']['video_id']
        self.room_group_name = f'comments_{self.video_id}'
        
        # Join video comment group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave video comment group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """
        Receive comment from WebSocket
        Expected format: {"type": "comment", "user": "username", "text": "comment text"}
        """
        data = json.loads(text_data)
        comment_type = data.get('type', 'comment')
        user = data.get('user', 'Anonymous')
        text = data.get('text', '')
        
        # Send comment to group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'comment_message',
                'user': user,
                'text': text,
                'timestamp': data.get('timestamp', '')
            }
        )
    
    async def comment_message(self, event):
        """
        Send comment to WebSocket
        """
        await self.send(text_data=json.dumps({
            'type': 'comment',
            'user': event['user'],
            'text': event['text'],
            'timestamp': event['timestamp']
        }))


class StreamConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for live video streaming
    Usage: ws://localhost:8000/ws/stream/{stream_id}/
    """
    
    async def connect(self):
        self.stream_id = self.scope['url_route']['kwargs']['stream_id']
        self.room_group_name = f'stream_{self.stream_id}'
        
        # Join streaming group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial connection message
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'message': f'Connected to stream {self.stream_id}'
        }))
    
    async def disconnect(self, close_code):
        # Leave streaming group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """
        Receive stream control messages
        Expected format: {"type": "control", "action": "play|pause|seek", "value": value}
        """
        data = json.loads(text_data)
        
        # Broadcast stream control to all viewers
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'stream_control',
                'action': data.get('action'),
                'value': data.get('value')
            }
        )
    
    async def stream_control(self, event):
        """
        Send stream control to WebSocket
        """
        await self.send(text_data=json.dumps({
            'type': 'control',
            'action': event['action'],
            'value': event.get('value')
        }))
    
    async def stream_data(self, event):
        """
        Send stream data chunks to WebSocket
        """
        await self.send(bytes_data=event['data'])
