"""
Visualization Module
Handles drawing bounding boxes, labels, and overlays on frames.
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
import logging


class Visualizer:
    """
    Handles visualization of detection results on frames.
    """
    
    def __init__(
        self,
        show_bbox: bool = True,
        show_label: bool = True,
        show_confidence: bool = True,
        show_track_id: bool = True,
        show_speed: bool = True,
        show_height: bool = True,
        show_distance: bool = True,
        show_direction: bool = True,
        show_fps: bool = True,
        bbox_thickness: int = 2,
        font_scale: float = 0.6,
        font_thickness: int = 2,
        colors: Optional[Dict[str, Tuple[int, int, int]]] = None
    ):
        """
        Initialize visualizer.
        
        Args:
            show_*: Flags to control what information to display
            bbox_thickness: Bounding box line thickness
            font_scale: Text font scale
            font_thickness: Text thickness
            colors: Dictionary mapping class names to BGR colors
        """
        self.logger = logging.getLogger(__name__)
        
        self.show_bbox = show_bbox
        self.show_label = show_label
        self.show_confidence = show_confidence
        self.show_track_id = show_track_id
        self.show_speed = show_speed
        self.show_height = show_height
        self.show_distance = show_distance
        self.show_direction = show_direction
        self.show_fps = show_fps
        
        self.bbox_thickness = bbox_thickness
        self.font_scale = font_scale
        self.font_thickness = font_thickness
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        
        # Default colors (BGR format)
        if colors is None:
            self.colors = {
                'person': (0, 255, 0),      # Green
                'car': (255, 0, 0),          # Blue
                'truck': (0, 0, 255),        # Red
                'bus': (0, 255, 255),        # Yellow
                'motorcycle': (255, 0, 255), # Magenta
                'bicycle': (255, 255, 0),    # Cyan
                'default': (255, 255, 255)   # White
            }
        else:
            self.colors = colors
        
        self.logger.info("Visualizer initialized")
    
    def draw_detections(
        self,
        frame: np.ndarray,
        detections: List[Dict],
        fps: Optional[float] = None
    ) -> np.ndarray:
        """
        Draw all detections on frame.
        
        Args:
            frame: Input frame
            detections: List of detections to draw
            fps: Current FPS for display
        
        Returns:
            Annotated frame
        """
        annotated_frame = frame.copy()
        
        # Draw each detection
        for det in detections:
            annotated_frame = self._draw_single_detection(annotated_frame, det)
        
        # Draw FPS
        if self.show_fps and fps is not None:
            self._draw_fps(annotated_frame, fps)
        
        # Draw info panel
        self._draw_info_panel(annotated_frame, detections)
        
        return annotated_frame
    
    def _draw_single_detection(
        self,
        frame: np.ndarray,
        detection: Dict
    ) -> np.ndarray:
        """
        Draw single detection on frame.
        
        Args:
            frame: Input frame
            detection: Detection dictionary
        
        Returns:
            Annotated frame
        """
        bbox = detection['bbox']
        class_name = detection['class_name']
        confidence = detection.get('confidence', 0)
        
        # Get color for this class
        color = self.colors.get(class_name, self.colors['default'])
        
        # Draw bounding box
        if self.show_bbox:
            x1, y1, x2, y2 = map(int, bbox)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, self.bbox_thickness)
        
        # Prepare label text
        label_parts = []
        
        if self.show_label:
            label_parts.append(class_name)
        
        if self.show_track_id and 'track_id' in detection:
            label_parts.append(f"ID:{detection['track_id']}")
        
        if self.show_confidence:
            label_parts.append(f"{confidence:.2f}")
        
        # Add estimation information
        info_parts = []
        
        if self.show_speed and 'speed_kmh' in detection and detection['speed_kmh'] is not None:
            info_parts.append(f"{detection['speed_kmh']} km/h")
        
        if self.show_height and 'height_cm' in detection and detection['height_cm'] is not None:
            info_parts.append(f"{detection['height_cm']} cm")
        
        if self.show_distance and 'distance_m' in detection and detection['distance_m'] is not None:
            info_parts.append(f"{detection['distance_m']} m")
        
        if self.show_direction and 'direction' in detection:
            direction = detection['direction']
            if direction != 'Stationary' and direction != 'Unknown':
                info_parts.append(direction)
        
        # Draw label
        if label_parts:
            label = ' | '.join(label_parts)
            self._draw_label(frame, bbox, label, color)
        
        # Draw additional info below bbox
        if info_parts:
            info_text = ' | '.join(info_parts)
            self._draw_info_text(frame, bbox, info_text, color)
        
        
        return frame
    
    def _draw_label(
        self,
        frame: np.ndarray,
        bbox: List[float],
        label: str,
        color: Tuple[int, int, int]
    ):
        """Draw label above bounding box."""
        x1, y1 = int(bbox[0]), int(bbox[1])
        
        # Get text size
        (text_width, text_height), baseline = cv2.getTextSize(
            label,
            self.font,
            self.font_scale,
            self.font_thickness
        )
        
        # Draw background rectangle
        cv2.rectangle(
            frame,
            (x1, y1 - text_height - baseline - 5),
            (x1 + text_width + 5, y1),
            color,
            -1
        )
        
        # Draw text
        cv2.putText(
            frame,
            label,
            (x1 + 2, y1 - baseline - 2),
            self.font,
            self.font_scale,
            (0, 0, 0),  # Black text
            self.font_thickness
        )
    
    def _draw_info_text(
        self,
        frame: np.ndarray,
        bbox: List[float],
        info: str,
        color: Tuple[int, int, int]
    ):
        """Draw additional info below bounding box."""
        x1, y2 = int(bbox[0]), int(bbox[3])
        
        # Get text size
        (text_width, text_height), baseline = cv2.getTextSize(
            info,
            self.font,
            self.font_scale * 0.8,
            self.font_thickness
        )
        
        # Draw background rectangle
        cv2.rectangle(
            frame,
            (x1, y2 + 2),
            (x1 + text_width + 5, y2 + text_height + baseline + 7),
            color,
            -1
        )
        
        # Draw text
        cv2.putText(
            frame,
            info,
            (x1 + 2, y2 + text_height + 4),
            self.font,
            self.font_scale * 0.8,
            (0, 0, 0),
            self.font_thickness
        )
    
    def _draw_fps(self, frame: np.ndarray, fps: float):
        """Draw FPS counter."""
        fps_text = f"FPS: {fps:.1f}"
        
        # Position at top-right
        (text_width, text_height), baseline = cv2.getTextSize(
            fps_text,
            self.font,
            self.font_scale,
            self.font_thickness
        )
        
        x = frame.shape[1] - text_width - 10
        y = text_height + 10
        
        # Draw background
        cv2.rectangle(
            frame,
            (x - 5, y - text_height - 5),
            (x + text_width + 5, y + baseline + 5),
            (0, 0, 0),
            -1
        )
        
        # Draw text
        cv2.putText(
            frame,
            fps_text,
            (x, y),
            self.font,
            self.font_scale,
            (0, 255, 0),
            self.font_thickness
        )
    
    def _draw_info_panel(self, frame: np.ndarray, detections: List[Dict]):
        """Draw information panel."""
        num_detections = len(detections)
        unique_classes = len(set(det['class_name'] for det in detections))
        
        info_text = f"Objects: {num_detections} | Classes: {unique_classes}"
        
        # Position at top-left
        x, y = 10, 30
        
        # Draw background
        (text_width, text_height), baseline = cv2.getTextSize(
            info_text,
            self.font,
            self.font_scale,
            self.font_thickness
        )
        
        cv2.rectangle(
            frame,
            (x - 5, y - text_height - 5),
            (x + text_width + 5, y + baseline + 5),
            (0, 0, 0),
            -1
        )
        
        # Draw text
        cv2.putText(
            frame,
            info_text,
            (x, y),
            self.font,
            self.font_scale,
            (255, 255, 255),
            self.font_thickness
        )
    
    
