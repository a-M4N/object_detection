"""
Vehicle Speed Estimator
Calculates real-world speed of vehicles using frame-to-frame displacement.

Mathematical Formula:
    Speed (km/h) = (Pixel Displacement × Scale Factor × FPS × 3.6) / 1000
    
    where:
    - Pixel Displacement = sqrt((x2-x1)² + (y2-y1)²)
    - Scale Factor = Real World Distance (m) / Pixel Distance
    - FPS = Frames per second
    - 3.6 = Conversion factor from m/s to km/h
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from collections import deque
import logging


class SpeedEstimator:
    """
    Estimates vehicle speed using frame-to-frame displacement and calibration.
    """
    
    def __init__(
        self,
        reference_distance_meters: float = 10.0,
        reference_distance_pixels: float = 200.0,
        fps: float = 30.0,
        smoothing_window: int = 5,
        vehicle_classes: Optional[List[str]] = None
    ):
        """
        Initialize speed estimator.
        
        Args:
            reference_distance_meters: Known real-world distance (meters)
            reference_distance_pixels: Corresponding pixel distance
            fps: Video frame rate
            smoothing_window: Number of frames to average for smooth speed
            vehicle_classes: List of vehicle class names to estimate speed for
        """
        self.logger = logging.getLogger(__name__)
        
        # Calibration parameters
        self.reference_distance_meters = reference_distance_meters
        self.reference_distance_pixels = reference_distance_pixels
        self.fps = fps
        self.smoothing_window = smoothing_window
        
        # Calculate scale factor (meters per pixel)
        self.scale_factor = reference_distance_meters / reference_distance_pixels
        
        # Vehicle classes to track
        if vehicle_classes is None:
            self.vehicle_classes = ['car', 'truck', 'bus', 'motorcycle', 'bicycle']
        else:
            self.vehicle_classes = vehicle_classes
        
        # Speed history for smoothing
        self.speed_history = {}  # track_id -> deque of speeds
        
        # Previous positions for displacement calculation
        self.previous_positions = {}  # track_id -> (x, y, frame_id)
        
        self.logger.info(f"Speed estimator initialized: scale={self.scale_factor:.4f} m/px, fps={fps}")
    
    def estimate_speed(
        self,
        tracked_objects: List[Dict],
        frame_id: int
    ) -> List[Dict]:
        """
        Estimate speed for tracked vehicles.
        
        Args:
            tracked_objects: List of tracked detections
            frame_id: Current frame number
        
        Returns:
            List of tracked objects with added 'speed_kmh' field
        """
        for obj in tracked_objects:
            # Check if object is a vehicle
            if obj['class_name'] not in self.vehicle_classes:
                obj['speed_kmh'] = None
                continue
            
            # Need track_id for speed calculation
            if 'track_id' not in obj:
                obj['speed_kmh'] = None
                continue
            
            track_id = obj['track_id']
            current_center = obj['center']
            
            # Calculate speed if we have previous position
            if track_id in self.previous_positions:
                prev_x, prev_y, prev_frame = self.previous_positions[track_id]
                
                # Calculate frame difference
                frame_diff = frame_id - prev_frame
                
                if frame_diff > 0 and frame_diff <= 5:  # Only use recent frames
                    # Calculate pixel displacement
                    dx = current_center[0] - prev_x
                    dy = current_center[1] - prev_y
                    pixel_displacement = np.sqrt(dx**2 + dy**2)
                    
                    # Convert to real-world displacement (meters)
                    real_displacement = pixel_displacement * self.scale_factor
                    
                    # Calculate speed (m/s)
                    time_elapsed = frame_diff / self.fps
                    speed_ms = real_displacement / time_elapsed if time_elapsed > 0 else 0
                    
                    # Convert to km/h
                    speed_kmh = speed_ms * 3.6
                    
                    # Add to speed history for smoothing
                    if track_id not in self.speed_history:
                        self.speed_history[track_id] = deque(maxlen=self.smoothing_window)
                    
                    self.speed_history[track_id].append(speed_kmh)
                    
                    # Calculate smoothed speed (average)
                    smoothed_speed = np.mean(list(self.speed_history[track_id]))
                    
                    obj['speed_kmh'] = round(smoothed_speed, 1)
                else:
                    obj['speed_kmh'] = None
            else:
                obj['speed_kmh'] = None
            
            # Update previous position
            self.previous_positions[track_id] = (
                current_center[0],
                current_center[1],
                frame_id
            )
        
        return tracked_objects
    
    def update_fps(self, fps: float):
        """Update video FPS."""
        self.fps = fps
        self.logger.info(f"FPS updated to {fps}")
    
