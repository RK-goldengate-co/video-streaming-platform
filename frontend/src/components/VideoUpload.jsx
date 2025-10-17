import React, { useState } from 'react';
import axios from 'axios';

const VideoUpload = () => {
  const [file, setFile] = useState(null);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.type.startsWith('video/')) {
      setFile(selectedFile);
      setMessage('');
    } else {
      setMessage('Please select a valid video file');
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setMessage('Please select a video file');
      return;
    }

    const formData = new FormData();
    formData.append('video', file);
    formData.append('title', title);
    formData.append('description', description);

    setUploading(true);
    setMessage('');

    try {
      const response = await axios.post('/api/videos/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Authorization': `Token ${localStorage.getItem('token')}`
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setUploadProgress(percentCompleted);
        },
      });

      setMessage('Video uploaded successfully!');
      setFile(null);
      setTitle('');
      setDescription('');
      setUploadProgress(0);
    } catch (error) {
      setMessage('Error uploading video: ' + (error.response?.data?.error || error.message));
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="video-upload-container">
      <h2>Upload Video</h2>
      
      <form onSubmit={handleUpload} className="upload-form">
        <div className="form-group">
          <label htmlFor="title">Video Title</label>
          <input
            type="text"
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Enter video title"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="description">Description</label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Enter video description"
            rows="4"
          />
        </div>

        <div className="form-group">
          <label htmlFor="video-file">Video File</label>
          <input
            type="file"
            id="video-file"
            accept="video/*"
            onChange={handleFileChange}
            required
          />
          {file && <p className="file-info">Selected: {file.name}</p>}
        </div>

        {uploading && (
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${uploadProgress}%` }}
            >
              {uploadProgress}%
            </div>
          </div>
        )}

        {message && (
          <div className={`message ${message.includes('Error') ? 'error' : 'success'}`}>
            {message}
          </div>
        )}

        <button 
          type="submit" 
          disabled={uploading}
          className="upload-button"
        >
          {uploading ? 'Uploading...' : 'Upload Video'}
        </button>
      </form>

      <style jsx>{`
        .video-upload-container {
          max-width: 600px;
          margin: 2rem auto;
          padding: 2rem;
          border: 1px solid #ddd;
          border-radius: 8px;
          background-color: #fff;
        }

        .upload-form {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }

        .form-group {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .form-group label {
          font-weight: 600;
          color: #333;
        }

        .form-group input,
        .form-group textarea {
          padding: 0.75rem;
          border: 1px solid #ccc;
          border-radius: 4px;
          font-size: 1rem;
        }

        .file-info {
          color: #666;
          font-size: 0.9rem;
        }

        .progress-bar {
          width: 100%;
          height: 30px;
          background-color: #e0e0e0;
          border-radius: 15px;
          overflow: hidden;
        }

        .progress-fill {
          height: 100%;
          background: linear-gradient(90deg, #4CAF50, #45a049);
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-weight: bold;
          transition: width 0.3s ease;
        }

        .message {
          padding: 1rem;
          border-radius: 4px;
          text-align: center;
        }

        .message.success {
          background-color: #d4edda;
          color: #155724;
        }

        .message.error {
          background-color: #f8d7da;
          color: #721c24;
        }

        .upload-button {
          padding: 1rem 2rem;
          background-color: #007bff;
          color: white;
          border: none;
          border-radius: 4px;
          font-size: 1rem;
          cursor: pointer;
          transition: background-color 0.3s;
        }

        .upload-button:hover:not(:disabled) {
          background-color: #0056b3;
        }

        .upload-button:disabled {
          background-color: #6c757d;
          cursor: not-allowed;
        }
      `}</style>
    </div>
  );
};

export default VideoUpload;
