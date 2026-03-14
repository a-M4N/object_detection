"""
PPE Detector Module
Detects whether required Personal Protective Equipment (PPE) is present on a person.
"""

import numpy as np
from typing import List, Dict
import logging
from models.detector import ObjectDetector

class PPEDetector:
    """
    Detects missing PPE items on a person.
    """
    
    def __init__(
        self,
        model_path: str,
        conf_threshold: float,
        iou_threshold: float,
        device: str,
        required_items: List[str],
        half: bool = False
    ):
        """Initialize the PPE Detector."""
        self.logger = logging.getLogger(__name__)
        self.required_items = [item.lower() for item in required_items]
        self.original_items = required_items
        
        try:
            self.detector = ObjectDetector(
                model_path=model_path,
                conf_threshold=conf_threshold,
                iou_threshold=iou_threshold,
                device=device,
                imgsz=640,  # using higher resolution as it runs on the full frame
                half=half
            )
            self.enabled = True
            self.logger.info(f"PPEDetector initialized with required items: {self.required_items}")
        except Exception as e:
            self.logger.error(f"Failed to initialize PPE detector: {e}")
            self.enabled = False
            
    def check_ppe(self, frame: np.ndarray, detections: List[Dict]) -> List[Dict]:
        """
        Check for PPE items directly in the main frame.
        Replaces the main people detections solely with the PPEs detected.
        
        Args:
            frame: Input frame
            detections: List of detections
        """
        if not self.enabled:
            return detections
            
        # Run PPE detection on the whole frame
        ppe_dets = self.detector.detect(frame)
        
        # Set all found items so visualization treats them as regular objects
        for p in ppe_dets:
            # Setting these just in case any downstream component expects it
            p['present_ppe'] = []
            
        return ppe_dets
