import React, { useRef, useEffect, useState } from 'react';
import videojs from 'video.js';
import 'video.js/dist/video-js.css';

const VideoPlayer = ({ videoId, videoUrl, title, autoplay = false }) => {
  const videoRef = useRef(null);
  const playerRef = useRef(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Initialize Video.js player
    if (!playerRef.current && videoRef.current) {
      const videoElement = videoRef.current;
      
      playerRef.current = videojs(videoElement, {
        controls: true,
        autoplay: autoplay,
        preload: 'auto',
        fluid: true,
        responsive: true,
        playbackRates: [0.5, 1, 1.5, 2],
        controlBar: {
          children: [
            'playToggle',
            'volumePanel',
            'currentTimeDisplay',
            'timeDivider',
            'durationDisplay',
            'progressControl',
            'remainingTimeDisplay',
            'playbackRateMenuButton',
            'qualitySelector',
            'fullscreenToggle'
          ]
        }
      }, () => {
        console.log('Video.js player ready');
        setIsLoading(false);
      });

      // Add event listeners
      playerRef.current.on('error', () => {
        console.error('Video player error');
      });

      playerRef.current.on('play', () => {
        console.log('Video playing');
      });

      playerRef.current.on('pause', () => {
        console.log('Video paused');
      });
    }

    // Cleanup
    return () => {
      if (playerRef.current) {
        playerRef.current.dispose();
        playerRef.current = null;
      }
    };
  }, [autoplay]);

  // Update video source when videoUrl changes
  useEffect(() => {
    if (playerRef.current && videoUrl) {
      playerRef.current.src({
        src: videoUrl,
        type: 'video/mp4'
      });
    }
  }, [videoUrl]);

  return (
    <div className="video-player-container">
      {title && <h2 className="video-title">{title}</h2>}
      
      <div className="video-wrapper">
        {isLoading && (
          <div className="loading-spinner">
            <div className="spinner"></div>
            <p>Loading video...</p>
          </div>
        )}
        
        <div data-vjs-player>
          <video
            ref={videoRef}
            className="video-js vjs-big-play-centered"
          />
        </div>
      </div>

      <style jsx>{`
        .video-player-container {
          max-width: 1200px;
          margin: 0 auto;
          padding: 1rem;
        }

        .video-title {
          margin-bottom: 1rem;
          color: #333;
          font-size: 1.5rem;
        }

        .video-wrapper {
          position: relative;
          width: 100%;
          padding-top: 56.25%; /* 16:9 aspect ratio */
          background-color: #000;
        }

        .video-wrapper > div[data-vjs-player] {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
        }

        .loading-spinner {
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          text-align: center;
          z-index: 10;
        }

        .spinner {
          border: 4px solid rgba(255, 255, 255, 0.3);
          border-top: 4px solid #fff;
          border-radius: 50%;
          width: 50px;
          height: 50px;
          animation: spin 1s linear infinite;
          margin: 0 auto 1rem;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        .loading-spinner p {
          color: #fff;
          font-size: 1rem;
        }

        /* Video.js customizations */
        :global(.video-js) {
          width: 100%;
          height: 100%;
        }

        :global(.vjs-big-play-button) {
          font-size: 3em;
          line-height: 1.5em;
          height: 1.5em;
          width: 3em;
          border-radius: 0.3em;
          background-color: rgba(0, 0, 0, 0.7);
          border: 0.06666em solid #fff;
        }

        :global(.vjs-big-play-button:hover) {
          background-color: rgba(0, 0, 0, 0.9);
        }
      `}</style>
    </div>
  );
};

export default VideoPlayer;
