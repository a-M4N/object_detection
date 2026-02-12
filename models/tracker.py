"""
Object Tracker using ByteTrack
Maintains object IDs across frames for multi-object tracking.
"""

import numpy as np
from typing import List, Dict, Optional
import logging
from collections import defaultdict, deque

try:
    import supervision as sv
    SUPERVISION_AVAILABLE = True
except ImportError:
    SUPERVISION_AVAILABLE = False
    logging.warning("Supervision library not available. Tracking will be disabled.")


class ObjectTracker:
    """
    Multi-object tracker using ByteTrack algorithm.
    
    Maintains unique IDs for detected objects across frames and tracks their trajectories.
    """
    
    def __init__(
        self,
        track_thresh: float = 0.5,
        track_buffer: int = 30,
        match_thresh: float = 0.8,
        min_box_area: int = 10
    ):
        """
        Initialize the object tracker.
        
        Args:
            track_thresh: Detection confidence threshold for tracking
            track_buffer: Number of frames to keep lost tracks
            match_thresh: Matching threshold for data association
            min_box_area: Minimum bounding box area to track
        """
        self.logger = logging.getLogger(__name__)
        
        if not SUPERVISION_AVAILABLE:
            self.logger.error("Supervision library not installed. Install with: pip install supervision")
            self.enabled = False
            return
        
        self.enabled = True
        self.track_thresh = track_thresh
        self.track_buffer = track_buffer
        self.match_thresh = match_thresh
        self.min_box_area = min_box_area
        
        # Initialize ByteTrack
        self.tracker = sv.ByteTrack(
            track_activation_threshold=track_thresh,
            lost_track_buffer=track_buffer,
            minimum_matching_threshold=match_thresh,
            frame_rate=30
        )
        
        # Track history for trajectory and speed calculation
        self.track_history = defaultdict(lambda: deque(maxlen=30))
        
        self.logger.info("ByteTrack tracker initialized successfully")
    
    def update(
        self,
        detections: List[Dict],
        frame_id: int
    ) -> List[Dict]:
        """
        Update tracker with new detections.
        
        Args:
            detections: List of detections from detector
            frame_id: Current frame number
        
        Returns:
            List of tracked objects with IDs
        """
        if not self.enabled or len(detections) == 0:
            return detections
        
        try:
            # Convert detections to supervision format
            boxes = []
            confidences = []
            class_ids = []
            
            for det in detections:
                bbox = det['bbox']
                # Filter by minimum box area
                width = bbox[2] - bbox[0]
                height = bbox[3] - bbox[1]
                if width * height < self.min_box_area:
                    continue
                
                boxes.append(bbox)
                confidences.append(det['confidence'])
                class_ids.append(det['class_id'])
            
            if len(boxes) == 0:
                return []
            
            # Create Detections object
            detections_sv = sv.Detections(
                xyxy=np.array(boxes),
                confidence=np.array(confidences),
                class_id=np.array(class_ids)
            )
            
            # Update tracker
            tracked_objects = self.tracker.update_with_detections(detections_sv)
            
            # Convert back to our format with track IDs
            tracked_detections = []
            for i in range(len(tracked_objects)):
                track_id = int(tracked_objects.tracker_id[i])
                bbox = tracked_objects.xyxy[i].tolist()
                
                # Calculate center point
                center_x = (bbox[0] + bbox[2]) / 2
                center_y = (bbox[1] + bbox[3]) / 2
                
                # Update track history
                self.track_history[track_id].append({
                    'frame_id': frame_id,
                    'center': (center_x, center_y),
                    'bbox': bbox
                })
                
                tracked_det = {
                    'bbox': bbox,
                    'confidence': float(tracked_objects.confidence[i]),
                    'class_id': int(tracked_objects.class_id[i]),
                    'class_name': detections[i]['class_name'] if i < len(detections) else 'unknown',
                    'track_id': track_id,
                    'center': (center_x, center_y)
                }
                tracked_detections.append(tracked_det)
            
            return tracked_detections
        
        except Exception as e:
            self.logger.error(f"Tracking update failed: {e}")
            # Return original detections without tracking
            return detections
    
    def get_track_history(self, track_id: int, num_frames: int = 10) -> List[Dict]:
        """
        Get historical positions for a track.
        
        Args:
            track_id: Track ID to query
            num_frames: Number of recent frames to return
        
        Returns:
            List of historical positions
        """
        if track_id not in self.track_history:
            return []
        
        history = list(self.track_history[track_id])
        return history[-num_frames:]
    
    def get_trajectory(self, track_id: int) -> List[tuple]:
        """
        Get trajectory (center points) for a track.
        
        Args:
            track_id: Track ID to query
        
        Returns:
            List of (x, y) center points
        """
        history = self.get_track_history(track_id)
        return [h['center'] for h in history]
    
    def get_active_tracks(self) -> List[int]:
        """
        Get list of currently active track IDs.
        
        Returns:
            List of active track IDs
        """
        return list(self.track_history.keys())
    
    def reset(self):
        """Reset tracker state."""
        if self.enabled:
            self.tracker = sv.ByteTrack(
                track_activation_threshold=self.track_thresh,
                lost_track_buffer=self.track_buffer,
                minimum_matching_threshold=self.match_thresh,
                frame_rate=30
            )
            self.track_history.clear()
            self.logger.info("Tracker reset")
    
    def cleanup_old_tracks(self, current_frame: int, max_age: int = 100):
        """
        Remove old tracks that haven't been updated recently.
        
        Args:
            current_frame: Current frame number
            max_age: Maximum age in frames before removal
        """
        tracks_to_remove = []
        
        for track_id, history in self.track_history.items():
            if len(history) > 0:
                last_frame = history[-1]['frame_id']
                if current_frame - last_frame > max_age:
                    tracks_to_remove.append(track_id)
        
        for track_id in tracks_to_remove:
            del self.track_history[track_id]
        
        if tracks_to_remove:
            self.logger.debug(f"Cleaned up {len(tracks_to_remove)} old tracks")
