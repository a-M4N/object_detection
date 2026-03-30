import cv2
import numpy as np
from ultralytics import YOLO
from typing import Dict, List, Tuple

# Configuration for PPE Detection (Optimized for Extreme High-Recall)
PPE_MODEL_PATH = "yolov8n-ppe.pt"  
CONF_THRESHOLD = 0.05    # Dropped to absolute minimum logical threshold to force tiny object recall
IOU_THRESHOLD = 0.65     # Increased to allow overlapping PPE on the same person (e.g., mask under goggles)

# Class-to-Color (BGR) Mapping (Curated for premium visualization)
PPE_COLORS = {
    "helmet": (0, 255, 255),         # Yellow (instead of Hardhat)
    "Vest": (0, 165, 255),           # Orange (instead of Safety Vest)
    "Gloves": (0, 255, 0),           # Green
    "goggles": (255, 0, 0),          # Blue (instead of Goggles)
    "safety_shoe": (19, 69, 139),    # Brown (instead of Boots)
    "mask": (255, 255, 255)          # White (instead of Mask)
}

# Global Model Instance for efficiency (Lazy Loading)
_ppe_model = None

def get_ppe_model():
    """Load the PPE model if not already loaded."""
    global _ppe_model
    if _ppe_model is None:
        try:
            # Load the model (YOLOv8/YOLOv11 compatible)
            _ppe_model = YOLO(PPE_MODEL_PATH)
        except Exception as e:
            # Fallback if specific PPE model is not found
            print(f"ERROR: Model file '{PPE_MODEL_PATH}' not found. Please ensure it is in the project root.")
            return None
    return _ppe_model

def detect_all_ppe(frame: np.ndarray) -> np.ndarray:
    """
    Integrate high-recall PPE detection with specialized visualization.
    
    Args:
        frame: Input BGR image from OpenCV
        
    Returns:
        np.ndarray: Processed frame with colored boxes, labels, and summary overlay.
    """
    model = get_ppe_model()
    if model is None:
        # Draw explicit error on the frame so the user knows why it's failing
        cv2.putText(frame, f"ERROR: MODEL NOT FOUND", (20, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)
        cv2.putText(frame, f"Missing: {PPE_MODEL_PATH}", (20, 90), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        return frame  # Return frame with error overlaid
            
    # Step 1: Image Pre-Processing Enhancement for Tiny Objects
    # Small/transparent items like goggles and masks often blend in. We create a highly 
    # contrasted copy of the frame to feed strictly to the model to make the edges pop!
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8,8))
    cl = clahe.apply(l)
    limg = cv2.merge((cl,a,b))
    enhanced_frame = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

    # Step 2: Perform High-Recall Inference
    # Fed with the custom 'enhanced_frame' while drawing boxes on the normal 'frame'.
    # augment=True (TTA), imgsz=1280 (Double Res) dramatically improves tiny object detection!
    results = model.predict(
        enhanced_frame, 
        conf=CONF_THRESHOLD, 
        iou=IOU_THRESHOLD, 
        augment=True,            # TTA: Critical for "different color, shape, etc."
        imgsz=1280,              # HUGE CHANGE: Doubled resolution to force detection of tiny objects (goggles/masks)
        agnostic_nms=False,      # Ensure classes don't suppress one another when stacked
        verbose=False
    )
    
    # Step 2: Loop through detection results
    if results and len(results) > 0 and results[0].boxes is not None:
        boxes = results[0].boxes
        class_names = model.names
        
        for i in range(len(boxes)):
            # Extract box coordinates, confidence, and class
            x1, y1, x2, y2 = map(int, boxes.xyxy[i].cpu().numpy())
            conf = float(boxes.conf[i].cpu().numpy())
            cls_id = int(boxes.cls[i].cpu().numpy())
            class_name = class_names[cls_id]
            
            # Select color based on class
            color = PPE_COLORS.get(class_name, (255, 255, 255))
            
            # A: Draw Bounding Box (Slightly thicker for premium look)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
            
            # B: Draw Label Panel with Confidence Percentage
            label_text = f"{class_name} {conf:.0%}"
            (w, h), b = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            
            # Label background rectangle (filled with class color)
            cv2.rectangle(frame, (x1, y1 - h - 10), (x1 + w + 5, y1), color, -1)
            # Label text (high contrast)
            cv2.putText(frame, label_text, (x1 + 2, y1 - 5), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

    # Summary overlay removed per user request.
    return frame
