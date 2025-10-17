// Login Form Component with Social Authentication
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './LoginForm.css';

const LoginForm = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (response.ok) {
        // Store token in localStorage
        localStorage.setItem('token', data.token);
        localStorage.setItem('user', JSON.stringify({
          id: data.user_id,
          username: data.username,
          email: data.email
        }));
        
        // Redirect to home
        navigate('/');
      } else {
        setError(data.error || 'Login failed');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = () => {
    window.location.href = '/api/auth/google/login';
  };

  const handleFacebookLogin = () => {
    window.location.href = '/api/auth/facebook/login';
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h2>Sign In</h2>
        
        {error && <div className="error-message">{error}</div>}
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username">Username or Email</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
              placeholder="Enter your username or email"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              placeholder="Enter your password"
            />
          </div>

          <button 
            type="submit" 
            className="btn-primary"
            disabled={loading}
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div className="divider">
          <span>OR</span>
        </div>

        <div className="social-login">
          <button 
            type="button" 
            className="btn-social btn-google"
            onClick={handleGoogleLogin}
          >
            <i className="fab fa-google"></i>
            Sign in with Google
          </button>

          <button 
            type="button" 
            className="btn-social btn-facebook"
            onClick={handleFacebookLogin}
          >
            <i className="fab fa-facebook-f"></i>
            Sign in with Facebook
          </button>
        </div>

        <div className="login-footer">
          <p>
            Don't have an account? 
            <a href="/register">Sign up</a>
          </p>
          <a href="/forgot-password" className="forgot-link">
            Forgot Password?
          </a>
        </div>
      </div>
    </div>
  );
};

export default LoginForm;
