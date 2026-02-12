"""
Direction Detector
Detects movement direction of tracked objects (left/right/forward/backward).

Uses trajectory analysis to determine object movement patterns.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from collections import deque
import logging


class DirectionDetector:
    """
    Detects movement direction of tracked objects using trajectory analysis.
    """
    
    def __init__(
        self,
        min_displacement: float = 10.0,
        history_frames: int = 10
    ):
        """
        Initialize direction detector.
        
        Args:
            min_displacement: Minimum pixel movement to detect direction
            history_frames: Number of frames to analyze for direction
        """
        self.logger = logging.getLogger(__name__)
        
        self.min_displacement = min_displacement
        self.history_frames = history_frames
        
        # Store position history for each track
        self.position_history = {}  # track_id -> deque of (x, y)
        
        self.logger.info(f"Direction detector initialized: min_disp={min_displacement}px")
    
    def detect_direction(
        self,
        tracked_objects: List[Dict]
    ) -> List[Dict]:
        """
        Detect movement direction for tracked objects.
        
        Args:
            tracked_objects: List of tracked detections
        
        Returns:
            List of tracked objects with added 'direction' and 'movement_vector' fields
        """
        for obj in tracked_objects:
            # Need track_id for direction detection
            if 'track_id' not in obj or 'center' not in obj:
                obj['direction'] = 'Unknown'
                obj['movement_vector'] = (0, 0)
                continue
            
            track_id = obj['track_id']
            current_center = obj['center']
            
            # Initialize history for new tracks
            if track_id not in self.position_history:
                self.position_history[track_id] = deque(maxlen=self.history_frames)
            
            # Add current position to history
            self.position_history[track_id].append(current_center)
            
            # Need at least 2 positions to determine direction
            if len(self.position_history[track_id]) < 2:
                obj['direction'] = 'Stationary'
                obj['movement_vector'] = (0, 0)
                continue
            
            # Calculate movement vector from first to last position in history
            positions = list(self.position_history[track_id])
            start_pos = positions[0]
            end_pos = positions[-1]
            
            dx = end_pos[0] - start_pos[0]
            dy = end_pos[1] - start_pos[1]
            
            # Calculate total displacement
            displacement = np.sqrt(dx**2 + dy**2)
            
            # Determine direction
            if displacement < self.min_displacement:
                direction = 'Stationary'
            else:
                # Calculate angle of movement
                angle = np.arctan2(dy, dx) * 180 / np.pi
                
                # Classify direction based on angle
                # 0° = Right, 90° = Down, 180° = Left, -90° = Up
                direction = self._angle_to_direction(angle, dx, dy)
            
            obj['direction'] = direction
            obj['movement_vector'] = (round(dx, 2), round(dy, 2))
        
        return tracked_objects
    
    def _angle_to_direction(self, angle: float, dx: float, dy: float) -> str:
        """
        Convert movement angle to direction label.
        
        Args:
            angle: Movement angle in degrees
            dx: Horizontal displacement
            dy: Vertical displacement
        
        Returns:
            Direction label
        """
        # Normalize angle to 0-360
        angle = angle % 360
        
        # Primary directions (8-way)
        if -22.5 <= angle < 22.5 or angle >= 337.5:
            return 'Right'
        elif 22.5 <= angle < 67.5:
            return 'Down-Right'
        elif 67.5 <= angle < 112.5:
            return 'Down'
        elif 112.5 <= angle < 157.5:
            return 'Down-Left'
        elif 157.5 <= angle < 202.5:
            return 'Left'
        elif 202.5 <= angle < 247.5:
            return 'Up-Left'
        elif 247.5 <= angle < 292.5:
            return 'Up'
        elif 292.5 <= angle < 337.5:
            return 'Up-Right'
        else:
            return 'Unknown'
    
    def get_simple_direction(self, direction: str) -> str:
        """
        Convert 8-way direction to simple 4-way direction.
        
        Args:
            direction: 8-way direction label
        
        Returns:
            Simple direction (Left/Right/Up/Down/Stationary)
        """
        if 'Left' in direction:
            return 'Left'
        elif 'Right' in direction:
            return 'Right'
        elif direction == 'Up':
            return 'Up'
        elif direction == 'Down':
            return 'Down'
        else:
            return direction
    
    def is_approaching(self, obj: Dict) -> bool:
        """
        Determine if object is approaching camera (getting larger).
        
        Args:
            obj: Tracked object with distance information
        
        Returns:
            True if approaching, False otherwise
        """
        if 'track_id' not in obj or 'distance_m' not in obj:
            return False
        
        track_id = obj['track_id']
        current_distance = obj.get('distance_m')
        
        if current_distance is None:
            return False
        
        # Check if we have distance history
        if not hasattr(self, 'distance_history'):
            self.distance_history = {}
        
        if track_id not in self.distance_history:
            self.distance_history[track_id] = deque(maxlen=5)
        
        self.distance_history[track_id].append(current_distance)
        
        # Need at least 2 measurements
        if len(self.distance_history[track_id]) < 2:
            return False
        
        # Check if distance is decreasing (approaching)
        distances = list(self.distance_history[track_id])
        return distances[-1] < distances[0]
    
    def get_velocity(self, track_id: int, fps: float = 30.0) -> Optional[Tuple[float, float]]:
        """
        Calculate velocity vector (pixels per second).
        
        Args:
            track_id: Track ID to query
            fps: Frames per second
        
        Returns:
            (vx, vy) velocity in pixels/second or None
        """
        if track_id not in self.position_history:
            return None
        
        positions = list(self.position_history[track_id])
        if len(positions) < 2:
            return None
        
        # Calculate velocity from first to last position
        start_pos = positions[0]
        end_pos = positions[-1]
        
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        
        # Convert to per-second velocity
        time_elapsed = len(positions) / fps
        vx = dx / time_elapsed if time_elapsed > 0 else 0
        vy = dy / time_elapsed if time_elapsed > 0 else 0
        
        return (round(vx, 2), round(vy, 2))
    
    def cleanup_old_tracks(self, active_track_ids: List[int]):
        """
        Remove data for tracks that are no longer active.
        
        Args:
            active_track_ids: List of currently active track IDs
        """
        inactive_tracks = set(self.position_history.keys()) - set(active_track_ids)
        for track_id in inactive_tracks:
            if track_id in self.position_history:
                del self.position_history[track_id]
            if hasattr(self, 'distance_history') and track_id in self.distance_history:
                del self.distance_history[track_id]
    
    def reset(self):
        """Reset direction detector state."""
        self.position_history.clear()
        if hasattr(self, 'distance_history'):
            self.distance_history.clear()
        self.logger.info("Direction detector reset")
