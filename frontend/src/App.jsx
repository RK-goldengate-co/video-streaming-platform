import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';

// Import pages (to be created)
// import HomePage from './pages/HomePage';
// import VideoPlayer from './pages/VideoPlayer';
// import Upload from './pages/Upload';
// import Dashboard from './pages/Dashboard';

function App() {
  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <h1>Video Streaming Platform</h1>
        </header>
        
        <main>
          <Routes>
            {/* Define routes here */}
            <Route path="/" element={
              <div className="home">
                <h2>Welcome to Video Streaming Platform</h2>
                <p>Upload, stream, and manage your video content</p>
              </div>
            } />
            
            {/* Uncomment when pages are created */}
            {/* <Route path="/" element={<HomePage />} /> */}
            {/* <Route path="/video/:id" element={<VideoPlayer />} /> */}
            {/* <Route path="/upload" element={<Upload />} /> */}
            {/* <Route path="/dashboard" element={<Dashboard />} /> */}
          </Routes>
        </main>
        
        <footer className="App-footer">
          <p>&copy; 2025 Video Streaming Platform</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
