"""
YOLO Object Detector Wrapper
Handles object detection using YOLOv8 models from Ultralytics.
"""

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
        imgsz: int = 640,
        half: bool = False
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
        self.half = half
        
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
                # letting classes=None handle all classes natively
                classes=classes, 
                device=self.device,
                imgsz=self.imgsz,
                half=self.half,
                augment=False,  # disabled TTA as it can merge/suppress overlapping multi-class detections
                agnostic_nms=False,  # strictly enforce per-class NMS
                max_det=300,
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
    
