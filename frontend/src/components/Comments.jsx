import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Comments = ({ videoId }) => {
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [ws, setWs] = useState(null);

  // Fetch comments from API
  useEffect(() => {
    fetchComments();
    
    // Setup WebSocket for real-time comments
    const websocket = new WebSocket(`ws://localhost:8000/ws/comments/${videoId}/`);
    
    websocket.onopen = () => {
      console.log('WebSocket connected for comments');
    };
    
    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'comment') {
        // Add new comment to the list
        setComments(prev => [...prev, {
          id: Date.now(),
          user: data.user,
          text: data.text,
          timestamp: data.timestamp
        }]);
      }
    };
    
    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    setWs(websocket);
    
    return () => {
      if (websocket) {
        websocket.close();
      }
    };
  }, [videoId]);

  const fetchComments = async () => {
    try {
      const response = await axios.get(`/api/videos/${videoId}/comments/`);
      setComments(response.data);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching comments:', err);
      setError('Failed to load comments');
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!newComment.trim()) {
      return;
    }

    setSubmitting(true);
    setError('');

    try {
      const token = localStorage.getItem('token');
      const username = localStorage.getItem('username') || 'Anonymous';
      
      // Send via WebSocket for real-time update
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
          type: 'comment',
          user: username,
          text: newComment,
          timestamp: new Date().toISOString()
        }));
      }
      
      // Also send to API for persistence
      await axios.post(
        `/api/videos/${videoId}/comments/`,
        { text: newComment },
        {
          headers: {
            'Authorization': `Token ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      setNewComment('');
    } catch (err) {
      console.error('Error posting comment:', err);
      setError('Failed to post comment');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (commentId) => {
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`/api/comments/${commentId}/`, {
        headers: {
          'Authorization': `Token ${token}`
        }
      });
      
      setComments(prev => prev.filter(c => c.id !== commentId));
    } catch (err) {
      console.error('Error deleting comment:', err);
      setError('Failed to delete comment');
    }
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = Math.floor((now - date) / 1000); // seconds
    
    if (diff < 60) return 'just now';
    if (diff < 3600) return `${Math.floor(diff / 60)} minutes ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)} hours ago`;
    return date.toLocaleDateString();
  };

  if (loading) {
    return <div className="comments-loading">Loading comments...</div>;
  }

  return (
    <div className="comments-container">
      <h3>Comments ({comments.length})</h3>
      
      <form onSubmit={handleSubmit} className="comment-form">
        <textarea
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          placeholder="Add a comment..."
          rows="3"
          disabled={submitting}
        />
        
        <button type="submit" disabled={submitting || !newComment.trim()}>
          {submitting ? 'Posting...' : 'Post Comment'}
        </button>
      </form>

      {error && <div className="error-message">{error}</div>}

      <div className="comments-list">
        {comments.length === 0 ? (
          <p className="no-comments">No comments yet. Be the first to comment!</p>
        ) : (
          comments.map((comment) => (
            <div key={comment.id} className="comment-item">
              <div className="comment-header">
                <span className="comment-user">{comment.user}</span>
                <span className="comment-timestamp">
                  {formatTimestamp(comment.timestamp)}
                </span>
              </div>
              <p className="comment-text">{comment.text}</p>
              {localStorage.getItem('username') === comment.user && (
                <button 
                  onClick={() => handleDelete(comment.id)}
                  className="delete-button"
                >
                  Delete
                </button>
              )}
            </div>
          ))
        )}
      </div>

      <style jsx>{`
        .comments-container {
          max-width: 800px;
          margin: 2rem auto;
          padding: 1rem;
        }

        h3 {
          margin-bottom: 1.5rem;
          color: #333;
        }

        .comment-form {
          margin-bottom: 2rem;
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .comment-form textarea {
          padding: 0.75rem;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 1rem;
          font-family: inherit;
          resize: vertical;
        }

        .comment-form button {
          align-self: flex-end;
          padding: 0.75rem 1.5rem;
          background-color: #007bff;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 1rem;
        }

        .comment-form button:hover:not(:disabled) {
          background-color: #0056b3;
        }

        .comment-form button:disabled {
          background-color: #6c757d;
          cursor: not-allowed;
        }

        .error-message {
          padding: 0.75rem;
          background-color: #f8d7da;
          color: #721c24;
          border-radius: 4px;
          margin-bottom: 1rem;
        }

        .comments-list {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .comment-item {
          padding: 1rem;
          border: 1px solid #e0e0e0;
          border-radius: 4px;
          background-color: #f9f9f9;
        }

        .comment-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 0.5rem;
        }

        .comment-user {
          font-weight: 600;
          color: #007bff;
        }

        .comment-timestamp {
          font-size: 0.875rem;
          color: #666;
        }

        .comment-text {
          margin: 0.5rem 0;
          color: #333;
          line-height: 1.5;
        }

        .delete-button {
          padding: 0.25rem 0.75rem;
          background-color: #dc3545;
          color: white;
          border: none;
          border-radius: 3px;
          font-size: 0.875rem;
          cursor: pointer;
        }

        .delete-button:hover {
          background-color: #c82333;
        }

        .no-comments {
          text-align: center;
          color: #666;
          padding: 2rem;
          font-style: italic;
        }

        .comments-loading {
          text-align: center;
          padding: 2rem;
          color: #666;
        }
      `}</style>
    </div>
  );
};

export default Comments;
