"""
Person Height Estimator
Estimates human height using bounding box dimensions and camera parameters.

Mathematical Formula:
    Height (m) = (Bbox Height × Distance × Sensor Height) / (Focal Length × Image Height)
    
    Simplified approach using reference height:
    Height (m) = (Bbox Height / Reference Bbox Height) × Reference Height
"""

import numpy as np
from typing import Dict, List, Optional
import logging


class HeightEstimator:
    """
    Estimates person height using bounding box analysis and camera calibration.
    """
    
    def __init__(
        self,
        average_person_height_cm: float = 170.0,
        camera_height_cm: float = 150.0,
        camera_angle_deg: float = 0.0,
        focal_length_pixels: float = 700.0,
        image_height: int = 720
    ):
        """
        Initialize height estimator.
        
        Args:
            average_person_height_cm: Reference person height (cm)
            camera_height_cm: Camera mounting height (cm)
            camera_angle_deg: Camera tilt angle (degrees, positive = downward)
            focal_length_pixels: Camera focal length in pixels
            image_height: Image height in pixels
        """
        self.logger = logging.getLogger(__name__)
        
        self.average_person_height_cm = average_person_height_cm
        self.camera_height_cm = camera_height_cm
        self.camera_angle_deg = camera_angle_deg
        self.focal_length_pixels = focal_length_pixels
        self.image_height = image_height
        
        # Reference bounding box height (will be calibrated from first detections)
        self.reference_bbox_height = None
        self.calibration_samples = []
        self.calibrated = False
        
        self.logger.info(f"Height estimator initialized: ref_height={average_person_height_cm}cm")
    
    def estimate_height(
        self,
        tracked_objects: List[Dict],
        distance_estimator=None
    ) -> List[Dict]:
        """
        Estimate height for persons.
        
        Args:
            tracked_objects: List of tracked detections
            distance_estimator: Optional distance estimator for more accurate height
        
        Returns:
            List of tracked objects with added 'height_cm' field
        """
        person_detections = []
        
        for obj in tracked_objects:
            # Only estimate height for persons
            if obj['class_name'] != 'person':
                obj['height_cm'] = None
                continue
            
            bbox = obj['bbox']
            bbox_height = bbox[3] - bbox[1]  # y2 - y1
            
            # Collect samples for calibration
            if not self.calibrated and len(self.calibration_samples) < 10:
                self.calibration_samples.append(bbox_height)
                if len(self.calibration_samples) == 10:
                    self._calibrate()
            
            # Estimate height
            if self.reference_bbox_height is not None:
                # Simple ratio-based estimation
                height_ratio = bbox_height / self.reference_bbox_height
                estimated_height = self.average_person_height_cm * height_ratio
                
                # Apply distance correction if available
                if distance_estimator is not None and 'distance_m' in obj and obj['distance_m'] is not None:
                    # Adjust for perspective (objects farther away appear smaller)
                    # This is a simplified correction
                    distance_m = obj['distance_m']
                    # Assume reference distance is 5 meters
                    reference_distance = 5.0
                    distance_correction = distance_m / reference_distance
                    estimated_height *= distance_correction
                
                # Clamp to reasonable range (100cm - 220cm)
                estimated_height = max(100, min(220, estimated_height))
                
                obj['height_cm'] = round(estimated_height, 1)
            else:
                # Use average height if not calibrated
                obj['height_cm'] = self.average_person_height_cm
            
            person_detections.append(obj)
        
        return tracked_objects
    
    def _calibrate(self):
        """
        Calibrate reference bounding box height from samples.
        Uses median to be robust to outliers.
        """
        if len(self.calibration_samples) > 0:
            self.reference_bbox_height = np.median(self.calibration_samples)
            self.calibrated = True
            self.logger.info(f"Height estimator calibrated: ref_bbox_height={self.reference_bbox_height:.1f}px")
    
    def estimate_height_with_distance(
        self,
        bbox_height_pixels: float,
        distance_meters: float
    ) -> float:
        """
        Estimate height using distance information (more accurate).
        
        Args:
            bbox_height_pixels: Bounding box height in pixels
            distance_meters: Distance from camera in meters
        
        Returns:
            Estimated height in centimeters
        
        Formula:
            Height = (bbox_height × distance) / focal_length
        """
        # Convert focal length to same units
        # Height in meters = (bbox_height_pixels × distance_meters) / focal_length_pixels
        height_meters = (bbox_height_pixels * distance_meters) / self.focal_length_pixels
        
        # Convert to centimeters
        height_cm = height_meters * 100
        
        # Clamp to reasonable range
        height_cm = max(100, min(220, height_cm))
        
        return round(height_cm, 1)
    
    def set_reference_height(self, height_cm: float):
        """
        Manually set reference person height.
        
        Args:
            height_cm: Reference height in centimeters
        """
        self.average_person_height_cm = height_cm
        self.logger.info(f"Reference height set to {height_cm}cm")
    
    def reset_calibration(self):
        """Reset calibration data."""
        self.reference_bbox_height = None
        self.calibration_samples = []
        self.calibrated = False
        self.logger.info("Height estimator calibration reset")
    
    def manual_calibrate(self, bbox_height: float, actual_height_cm: float):
        """
        Manually calibrate using a known person's height.
        
        Args:
            bbox_height: Bounding box height in pixels
            actual_height_cm: Actual height in centimeters
        """
        # Calculate reference bbox height for average person
        self.reference_bbox_height = bbox_height * (self.average_person_height_cm / actual_height_cm)
        self.calibrated = True
        self.logger.info(f"Manual calibration: ref_bbox_height={self.reference_bbox_height:.1f}px")
