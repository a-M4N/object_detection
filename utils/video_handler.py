"""
Video Handler
Handles video input/output operations for various sources.
"""

import cv2
import numpy as np
from typing import Optional, Tuple, Union
import logging
from pathlib import Path


class VideoHandler:
    """
    Handles video input from files, webcam, and IP cameras.
    Also handles video output for saving results.
    """
    
    def __init__(
        self,
        source: Union[str, int],
        mode: str = 'video'
    ):
        """
        Initialize video handler.
        
        Args:
            source: Video source (file path, webcam index, or RTSP URL)
            mode: Input mode ('image', 'video', 'webcam', 'stream')
        """
        self.logger = logging.getLogger(__name__)
        self.source = source
        self.mode = mode
        self.cap = None
        self.writer = None
        self.fps = 30.0
        self.frame_width = 0
        self.frame_height = 0
        self.total_frames = 0
        self.current_frame = 0
        
        self._initialize_source()
    
    def _initialize_source(self):
        """Initialize video source based on mode."""
        try:
            if self.mode == 'image':
                # For images, we'll read directly
                self.logger.info(f"Image mode: {self.source}")
                return
            
            # For video, webcam, and stream
            if self.mode == 'webcam':
                self.source = int(self.source) if isinstance(self.source, str) else self.source
                self.logger.info(f"Opening webcam: {self.source}")
            elif self.mode == 'stream':
                self.logger.info(f"Opening stream: {self.source}")
            else:
                self.logger.info(f"Opening video file: {self.source}")
            
            self.cap = cv2.VideoCapture(self.source)
            
            if not self.cap.isOpened():
                raise ValueError(f"Failed to open video source: {self.source}")
            
            # Get video properties
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            if self.fps == 0 or self.fps > 120:  # Invalid FPS
                self.fps = 30.0
                self.logger.warning(f"Invalid FPS detected, using default: {self.fps}")
            
            self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            self.logger.info(f"Video properties: {self.frame_width}x{self.frame_height} @ {self.fps} FPS")
            if self.total_frames > 0:
                self.logger.info(f"Total frames: {self.total_frames}")
        
        except Exception as e:
            self.logger.error(f"Failed to initialize video source: {e}")
            raise
    
    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Read next frame from source.
        
        Returns:
            Tuple of (success, frame)
        """
        if self.mode == 'image':
            # Read image file
            frame = cv2.imread(str(self.source))
            if frame is not None:
                self.frame_height, self.frame_width = frame.shape[:2]
                return True, frame
            return False, None
        
        if self.cap is None:
            return False, None
        
        ret, frame = self.cap.read()
        if ret:
            self.current_frame += 1
        
        return ret, frame
    
    def read_image(self) -> Optional[np.ndarray]:
        """
        Read single image.
        
        Returns:
            Image array or None
        """
        frame = cv2.imread(str(self.source))
        if frame is not None:
            self.frame_height, self.frame_width = frame.shape[:2]
        return frame
    
    def initialize_writer(
        self,
        output_path: str,
        codec: str = 'mp4v',
        fps: Optional[float] = None
    ):
        """
        Initialize video writer for saving output.
        
        Args:
            output_path: Output video file path
            codec: Video codec (mp4v, avc1, h264)
            fps: Output FPS (uses input FPS if None)
        """
        try:
            # Create output directory if needed
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Use input FPS if not specified
            if fps is None:
                fps = self.fps
            
            # Define codec
            fourcc = cv2.VideoWriter_fourcc(*codec)
            
            # Initialize writer
            self.writer = cv2.VideoWriter(
                output_path,
                fourcc,
                fps,
                (self.frame_width, self.frame_height)
            )
            
            if not self.writer.isOpened():
                raise ValueError(f"Failed to initialize video writer: {output_path}")
            
            self.logger.info(f"Video writer initialized: {output_path}")
        
        except Exception as e:
            self.logger.error(f"Failed to initialize video writer: {e}")
            raise
    
    def write_frame(self, frame: np.ndarray):
        """
        Write frame to output video.
        
        Args:
            frame: Frame to write
        """
        if self.writer is not None:
            self.writer.write(frame)
    
    def release(self):
        """Release video capture and writer resources."""
        if self.cap is not None:
            self.cap.release()
            self.logger.info("Video capture released")
        
        if self.writer is not None:
            self.writer.release()
            self.logger.info("Video writer released")
    
    def get_progress(self) -> float:
        """
        Get processing progress (0-100%).
        
        Returns:
            Progress percentage
        """
        if self.total_frames > 0:
            return (self.current_frame / self.total_frames) * 100
        return 0.0
    
    def seek_frame(self, frame_number: int) -> bool:
        """
        Seek to specific frame.
        
        Args:
            frame_number: Frame number to seek to
        
        Returns:
            True if successful
        """
        if self.cap is not None and self.mode == 'video':
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            self.current_frame = frame_number
            return True
        return False
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release()
