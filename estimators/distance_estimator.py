"""
Distance Estimator
Estimates distance of objects from camera using bounding box size and known object dimensions.

Mathematical Formula:
    Distance (m) = (Known Object Height × Focal Length) / Bbox Height in Pixels
    
    where:
    - Known Object Height: Real-world height of the object (meters)
    - Focal Length: Camera focal length (pixels)
    - Bbox Height: Bounding box height (pixels)
"""

import numpy as np
from typing import Dict, List, Optional
import logging


class DistanceEstimator:
    """
    Estimates distance of objects from camera using pinhole camera model.
    """
    
    def __init__(
        self,
        focal_length_pixels: float = 700.0,
        known_object_heights: Optional[Dict[str, float]] = None
    ):
        """
        Initialize distance estimator.
        
        Args:
            focal_length_pixels: Camera focal length in pixels
            known_object_heights: Dictionary mapping class names to real-world heights (meters)
        """
        self.logger = logging.getLogger(__name__)
        
        self.focal_length_pixels = focal_length_pixels
        
        # Default known object heights (in meters)
        if known_object_heights is None:
            self.known_object_heights = {
                'person': 1.7,
                'car': 1.5,
                'truck': 3.0,
                'bus': 3.5,
                'bicycle': 1.0,
                'motorcycle': 1.2,
                'dog': 0.6,
                'cat': 0.3,
                'horse': 1.6,
                'cow': 1.5
            }
        else:
            self.known_object_heights = known_object_heights
        
        self.logger.info(f"Distance estimator initialized: focal_length={focal_length_pixels}px")
        self.logger.info(f"Known object heights: {list(self.known_object_heights.keys())}")
    
    def estimate_distance(
        self,
        tracked_objects: List[Dict]
    ) -> List[Dict]:
        """
        Estimate distance for tracked objects.
        
        Args:
            tracked_objects: List of tracked detections
        
        Returns:
            List of tracked objects with added 'distance_m' field
        """
        for obj in tracked_objects:
            class_name = obj['class_name']
            
            # Check if we have known height for this class
            if class_name not in self.known_object_heights:
                obj['distance_m'] = None
                continue
            
            bbox = obj['bbox']
            bbox_height = bbox[3] - bbox[1]  # y2 - y1
            
            if bbox_height <= 0:
                obj['distance_m'] = None
                continue
            
            # Get known object height
            known_height = self.known_object_heights[class_name]
            
            # Calculate distance using pinhole camera model
            # Distance = (Known Height × Focal Length) / Bbox Height
            distance = (known_height * self.focal_length_pixels) / bbox_height
            
            # Clamp to reasonable range (0.5m - 100m)
            distance = max(0.5, min(100.0, distance))
            
            obj['distance_m'] = round(distance, 2)
        
        return tracked_objects
    
    def estimate_distance_single(
        self,
        class_name: str,
        bbox_height: float
    ) -> Optional[float]:
        """
        Estimate distance for a single object.
        
        Args:
            class_name: Object class name
            bbox_height: Bounding box height in pixels
        
        Returns:
            Estimated distance in meters or None
        """
        if class_name not in self.known_object_heights or bbox_height <= 0:
            return None
        
        known_height = self.known_object_heights[class_name]
        distance = (known_height * self.focal_length_pixels) / bbox_height
        distance = max(0.5, min(100.0, distance))
        
        return round(distance, 2)
    
    def update_focal_length(self, focal_length_pixels: float):
        """
        Update camera focal length.
        
        Args:
            focal_length_pixels: New focal length in pixels
        """
        self.focal_length_pixels = focal_length_pixels
        self.logger.info(f"Focal length updated to {focal_length_pixels}px")
    
    def add_known_object(self, class_name: str, height_meters: float):
        """
        Add or update known object height.
        
        Args:
            class_name: Object class name
            height_meters: Real-world height in meters
        """
        self.known_object_heights[class_name] = height_meters
        self.logger.info(f"Added/updated known object: {class_name} = {height_meters}m")
    
    def calibrate_focal_length(
        self,
        known_distance_meters: float,
        bbox_height_pixels: float,
        object_height_meters: float
    ) -> float:
        """
        Calibrate focal length using a known distance measurement.
        
        Args:
            known_distance_meters: Measured distance to object
            bbox_height_pixels: Bounding box height in pixels
            object_height_meters: Known object height in meters
        
        Returns:
            Calibrated focal length in pixels
        
        Formula:
            Focal Length = (Distance × Bbox Height) / Object Height
        """
        focal_length = (known_distance_meters * bbox_height_pixels) / object_height_meters
        self.focal_length_pixels = focal_length
        self.logger.info(f"Focal length calibrated to {focal_length:.1f}px")
        return focal_length
    
    def get_distance_zone(self, distance_m: Optional[float]) -> str:
        """
        Categorize distance into zones.
        
        Args:
            distance_m: Distance in meters
        
        Returns:
            Distance zone label
        """
        if distance_m is None:
            return "Unknown"
        elif distance_m < 2:
            return "Very Close"
        elif distance_m < 5:
            return "Close"
        elif distance_m < 10:
            return "Medium"
        elif distance_m < 20:
            return "Far"
        else:
            return "Very Far"
