# Video Streaming Platform

## Mô tả dự án

Nền tảng phát video toàn diện với các tính năng:

- **Upload Video**: Tải lên và quản lý video
- **Phát trực tuyến**: Streaming video chất lượng cao
- **User Management**: Quản lý người dùng và phân quyền
- **Bình luận**: Hệ thống comment và tương tác
- **Streaming Real-time**: Phát trực tiếp video
- **Danh mục Video**: Phân loại và tổ chức nội dung
- **Dashboard Admin**: Quản trị hệ thống toàn diện

## Cấu trúc dự án

```
video-streaming-platform/
├── backend/              # API RESTful
│   ├── api/             # Endpoints
│   ├── models/          # Database models
│   ├── services/        # Business logic
│   └── requirements.txt
├── frontend/            # React application
│   ├── src/
│   │   ├── components/  # UI components
│   │   ├── pages/       # Page components
│   │   └── services/    # API services
│   └── package.json
├── data/                # Sample data
├── scripts/             # Management tools
└── README.md
```

## Công nghệ sử dụng

### Backend
- Django/FastAPI
- PostgreSQL
- Redis (caching)
- FFmpeg (video processing)

### Frontend
- React.js
- Video.js (player)
- Material-UI/Tailwind CSS

## Cài đặt

### Backend
```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend
```bash
cd frontend
npm install
npm start
```

## Tính năng chính

1. **Video Player**: Giao diện phát video mượt mà
2. **Upload System**: Tải lên video với progress tracking
3. **Comment System**: Bình luận và thảo luận
4. **Admin Dashboard**: Quản lý video, user, thống kê
5. **Real-time Streaming**: Phát trực tiếp với WebRTC
6. **Category Management**: Quản lý danh mục video

## License

MIT License

## Đóng góp

Mọi đóng góp đều được chào đón. Vui lòng tạo pull request.
