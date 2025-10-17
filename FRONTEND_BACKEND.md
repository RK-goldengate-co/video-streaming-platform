# Frontend-Backend Integration Guide

## Overview

This guide explains how to integrate the React frontend with the Django/FastAPI backend for the video streaming platform.

## Backend Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

Required packages:
- Django >= 4.0 or FastAPI >= 0.95
- djangorestframework
- django-cors-headers
- channels (for WebSocket support)
- channels-redis
- Pillow (for image processing)
- psycopg2-binary (PostgreSQL)

### 2. Configure CORS

In your Django `settings.py`:

```python
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'channels',
    # your apps
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # ...
]

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React dev server
    "http://localhost:5173",  # Vite dev server
]

CORS_ALLOW_CREDENTIALS = True

# Channels Configuration for WebSocket
ASGI_APPLICATION = 'backend.asgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
```

### 3. URL Configuration

In your main `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),  # Include API routes
]
```

### 4. WebSocket Routing

Create `routing.py` in your backend:

```python
from django.urls import path
from api.websocket_handlers import CommentConsumer, StreamConsumer

websocket_urlpatterns = [
    path('ws/comments/<int:video_id>/', CommentConsumer.as_asgi()),
    path('ws/stream/<int:stream_id>/', StreamConsumer.as_asgi()),
]
```

### 5. Run Backend Server

```bash
# Development
python manage.py runserver

# Production (with Daphne for WebSocket support)
daphne -b 0.0.0.0 -p 8000 backend.asgi:application
```

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

Required packages:
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.4.0",
    "video.js": "^8.3.0",
    "react-router-dom": "^6.11.0"
  }
}
```

### 2. API Configuration

Create `src/services/api.js`:

```javascript
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default api;
```

### 3. Environment Variables

Create `.env` file in frontend root:

```env
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_WS_URL=ws://localhost:8000/ws
```

### 4. Using Components

#### Example App.jsx:

```javascript
import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import VideoUpload from './components/VideoUpload';
import VideoPlayer from './components/VideoPlayer';
import Comments from './components/Comments';

function App() {
  return (
    <BrowserRouter>
      <div className="App">
        <Routes>
          <Route path="/upload" element={<VideoUpload />} />
          <Route 
            path="/video/:id" 
            element={
              <>
                <VideoPlayer 
                  videoId={1} 
                  videoUrl="http://localhost:8000/api/videos/1/stream/"
                  title="Sample Video"
                />
                <Comments videoId={1} />
              </>
            } 
          />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
```

## API Endpoints

### Authentication

- **POST** `/api/register/` - Register new user
  ```json
  {"username": "string", "email": "string", "password": "string"}
  ```

- **POST** `/api/login/` - Login user
  ```json
  {"username": "string", "password": "string"}
  ```
  Returns: `{"user_id": int, "username": string, "token": string}`

### Videos

- **GET** `/api/videos/` - List all videos
- **POST** `/api/videos/upload/` - Upload video (multipart/form-data)
- **GET** `/api/videos/{id}/stream/` - Stream video

### Comments

- **GET** `/api/videos/{id}/comments/` - Get video comments
- **POST** `/api/videos/{id}/comments/` - Post comment
- **DELETE** `/api/comments/{id}/` - Delete comment

## WebSocket Integration

### Real-time Comments

```javascript
const ws = new WebSocket(`ws://localhost:8000/ws/comments/${videoId}/`);

ws.onopen = () => {
  console.log('Connected to comments');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Handle incoming comment
};

// Send comment
ws.send(JSON.stringify({
  type: 'comment',
  user: 'username',
  text: 'comment text',
  timestamp: new Date().toISOString()
}));
```

### Live Streaming

```javascript
const streamWs = new WebSocket(`ws://localhost:8000/ws/stream/${streamId}/`);

streamWs.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'control') {
    // Handle stream control
  }
};
```

## Authentication Flow

1. User registers/logs in via `/api/register/` or `/api/login/`
2. Backend returns authentication token
3. Frontend stores token in localStorage
4. Token is automatically added to all API requests via axios interceptor
5. Token is sent with WebSocket connections for authenticated features

## File Upload Flow

1. User selects video file in VideoUpload component
2. File is sent via FormData to `/api/videos/upload/`
3. Backend processes video and stores it
4. Progress is tracked via axios onUploadProgress
5. Backend returns video metadata

## Video Streaming Flow

1. Frontend requests video via `/api/videos/{id}/stream/`
2. Backend streams video using StreamingHttpResponse
3. Video.js player handles adaptive streaming
4. Playback controls and quality selection available

## Deployment Considerations

### Backend
- Use Gunicorn/Uvicorn for production WSGI
- Use Daphne for WebSocket support (ASGI)
- Configure Nginx as reverse proxy
- Set up Redis for Channels layer
- Use PostgreSQL for production database
- Configure media file storage (S3, CloudFront)

### Frontend
- Build: `npm run build`
- Serve static files via Nginx/CDN
- Update environment variables for production URLs
- Enable production optimizations

## Troubleshooting

### CORS Issues
- Verify CORS_ALLOWED_ORIGINS includes your frontend URL
- Check that django-cors-headers is properly installed and configured

### WebSocket Connection Failed
- Ensure Redis is running for Channels
- Verify WebSocket URL format (ws:// not http://)
- Check firewall/proxy settings

### Video Not Playing
- Verify video file format (MP4 recommended)
- Check MIME types in server configuration
- Ensure video file exists and is accessible

### Authentication Issues
- Verify token is being stored and sent correctly
- Check token format ("Token <token>" for DRF)
- Ensure REST framework authentication is configured

## Additional Resources

- [Django REST Framework Documentation](https://www.django-rest-framework.org/)
- [Django Channels Documentation](https://channels.readthedocs.io/)
- [Video.js Documentation](https://videojs.com/)
- [Axios Documentation](https://axios-http.com/)
- [React Router Documentation](https://reactrouter.com/)
