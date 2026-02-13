"""
Object Tracker using ByteTrack
Maintains object IDs across frames for multi-object tracking.
"""

import numpy as np
from typing import List, Dict, Optional
import logging

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
