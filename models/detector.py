"""
YOLO Object Detector Wrapper
Handles object detection using YOLOv8 models from Ultralytics.
"""

import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Dict, Tuple, Optional
import logging


class ObjectDetector:
    """
    Wrapper class for YOLOv8 object detection.
    
    Attributes:
        model: YOLO model instance
        conf_threshold: Confidence threshold for detections
        iou_threshold: IOU threshold for Non-Maximum Suppression
        device: Device to run inference on (cuda/cpu)
        class_names: List of class names from COCO dataset
    """
    
    def __init__(
        self,
        model_path: str = "yolov8m.pt",
        conf_threshold: float = 0.5,
        iou_threshold: float = 0.45,
        device: str = "cuda",
        imgsz: int = 640
    ):
        """
        Initialize the YOLO detector.
        
        Args:
            model_path: Path to YOLO model weights
            conf_threshold: Minimum confidence for detections
            iou_threshold: IOU threshold for NMS
            device: Device for inference (cuda/cpu)
            imgsz: Input image size for model
        """
        self.logger = logging.getLogger(__name__)
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.device = device
        self.imgsz = imgsz
        
        # Load YOLO model
        self.logger.info(f"Loading YOLO model: {model_path}")
        try:
            self.model = YOLO(model_path)
            self.model.to(device)
            self.class_names = self.model.names
            self.logger.info(f"Model loaded successfully on {device}")
            self.logger.info(f"Detected {len(self.class_names)} classes")
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            raise
    
    def detect(
        self,
        frame: np.ndarray,
        classes: Optional[List[int]] = None
    ) -> List[Dict]:
        """
        Perform object detection on a single frame.
        
        Args:
            frame: Input image (BGR format)
            classes: Optional list of class IDs to detect
        
        Returns:
            List of detections, each containing:
                - bbox: [x1, y1, x2, y2]
                - confidence: Detection confidence
                - class_id: Class ID
                - class_name: Class name
        """
        try:
            # Run inference
            results = self.model.predict(
                frame,
                conf=self.conf_threshold,
                iou=self.iou_threshold,
                classes=classes,
                device=self.device,
                imgsz=self.imgsz,
                verbose=False
            )
            
            # Parse results
            detections = []
            if len(results) > 0 and results[0].boxes is not None:
                boxes = results[0].boxes
                
                for i in range(len(boxes)):
                    # Extract box coordinates
                    box = boxes.xyxy[i].cpu().numpy()
                    conf = float(boxes.conf[i].cpu().numpy())
                    cls_id = int(boxes.cls[i].cpu().numpy())
                    
                    detection = {
                        'bbox': box.tolist(),  # [x1, y1, x2, y2]
                        'confidence': conf,
                        'class_id': cls_id,
                        'class_name': self.class_names[cls_id]
                    }
                    detections.append(detection)
            
            return detections
        
        except Exception as e:
            self.logger.error(f"Detection failed: {e}")
            return []
    
    def detect_batch(
        self,
        frames: List[np.ndarray],
        classes: Optional[List[int]] = None
    ) -> List[List[Dict]]:
        """
        Perform batch detection on multiple frames.
        
        Args:
            frames: List of input images
            classes: Optional list of class IDs to detect
        
        Returns:
            List of detection lists for each frame
        """
        try:
            results = self.model.predict(
                frames,
                conf=self.conf_threshold,
                iou=self.iou_threshold,
                classes=classes,
                device=self.device,
                imgsz=self.imgsz,
                verbose=False
            )
            
            all_detections = []
            for result in results:
                detections = []
                if result.boxes is not None:
                    boxes = result.boxes
                    
                    for i in range(len(boxes)):
                        box = boxes.xyxy[i].cpu().numpy()
                        conf = float(boxes.conf[i].cpu().numpy())
                        cls_id = int(boxes.cls[i].cpu().numpy())
                        
                        detection = {
                            'bbox': box.tolist(),
                            'confidence': conf,
                            'class_id': cls_id,
                            'class_name': self.class_names[cls_id]
                        }
                        detections.append(detection)
                
                all_detections.append(detections)
            
            return all_detections
        
        except Exception as e:
            self.logger.error(f"Batch detection failed: {e}")
            return [[] for _ in frames]
    
    def get_class_id(self, class_name: str) -> Optional[int]:
        """
        Get class ID from class name.
        
        Args:
            class_name: Name of the class
        
        Returns:
            Class ID or None if not found
        """
        for cls_id, name in self.class_names.items():
            if name.lower() == class_name.lower():
                return cls_id
        return None
    
    def get_class_ids(self, class_names: List[str]) -> List[int]:
        """
        Get class IDs from list of class names.
        
        Args:
            class_names: List of class names
        
        Returns:
            List of class IDs
        """
        class_ids = []
        for name in class_names:
            cls_id = self.get_class_id(name)
            if cls_id is not None:
                class_ids.append(cls_id)
        return class_ids
    
    def update_confidence_threshold(self, threshold: float):
        """Update confidence threshold."""
        self.conf_threshold = max(0.0, min(1.0, threshold))
        self.logger.info(f"Confidence threshold updated to {self.conf_threshold}")
    
    def update_iou_threshold(self, threshold: float):
        """Update IOU threshold."""
        self.iou_threshold = max(0.0, min(1.0, threshold))
        self.logger.info(f"IOU threshold updated to {self.iou_threshold}")
