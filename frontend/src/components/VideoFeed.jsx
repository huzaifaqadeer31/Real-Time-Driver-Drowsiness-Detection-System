const VideoFeed = () => {
  return (
    <div className="video-section">
      <div className="video-wrapper">
        <img src="http://127.0.0.1:5000/video_feed" alt="Live Video Feed" id="videoFeed" />
        <div className="scan-line"></div>
      </div>
    </div>
  );
};

export default VideoFeed;
