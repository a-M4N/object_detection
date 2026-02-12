"""
Demo Script
Demonstrates the object detection system with a simple example.
"""

import cv2
import numpy as np
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from models.detector import ObjectDetector
from models.tracker import ObjectTracker
from estimators.speed_estimator import SpeedEstimator
from estimators.distance_estimator import DistanceEstimator
from utils.visualization import Visualizer


def create_demo_video():
    """Create a simple demo video with moving objects."""
    print("Creating demo video...")
    
    # Video parameters
    width, height = 1280, 720
    fps = 30
    duration = 10  # seconds
    total_frames = fps * duration
    
    # Create video writer
    output_path = "demo_input.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    for frame_num in range(total_frames):
        # Create frame
        frame = np.ones((height, width, 3), dtype=np.uint8) * 50
        
        # Draw road
        cv2.rectangle(frame, (0, height//2), (width, height), (80, 80, 80), -1)
        
        # Draw lane markings
        for x in range(0, width, 100):
            cv2.rectangle(frame, (x, height//2 + 50), (x + 50, height//2 + 60), (255, 255, 255), -1)
        
        # Moving car
        car_x = int((frame_num / total_frames) * width)
        car_y = height // 2 + 100
        cv2.rectangle(frame, (car_x, car_y), (car_x + 100, car_y + 60), (0, 0, 255), -1)
        cv2.rectangle(frame, (car_x + 10, car_y + 10), (car_x + 40, car_y + 40), (200, 200, 255), -1)
        cv2.rectangle(frame, (car_x + 60, car_y + 10), (car_x + 90, car_y + 40), (200, 200, 255), -1)
        
        # Add text
        cv2.putText(frame, f"Frame: {frame_num}/{total_frames}", (20, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        out.write(frame)
    
    out.release()
    print(f"Demo video created: {output_path}")
    return output_path


def run_simple_demo():
    """Run a simple detection demo without all features."""
    print("\n" + "="*60)
    print("Simple Object Detection Demo")
    print("="*60 + "\n")
    
    # Check if webcam is available
    print("Checking webcam availability...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Webcam not available. Please connect a webcam or use a video file.")
        cap.release()
        return
    
    print("✓ Webcam found!")
    
    # Initialize detector
    print("\nInitializing YOLO detector...")
    try:
        detector = ObjectDetector(
            model_path="yolov8n.pt",
            conf_threshold=0.5,
            device="cuda"  # Change to "cpu" if no GPU
        )
        print("✓ Detector initialized")
    except Exception as e:
        print(f"✗ Failed to initialize detector: {e}")
        cap.release()
        return
    
    # Initialize visualizer
    visualizer = Visualizer()
    
    print("\n" + "="*60)
    print("Starting detection... Press 'Q' to quit")
    print("="*60 + "\n")
    
    frame_count = 0
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detect objects
            detections = detector.detect(frame)
            
            # Visualize
            annotated_frame = visualizer.draw_detections(frame, detections)
            
            # Display
            cv2.imshow('Object Detection Demo', annotated_frame)
            
            # Print detections every 30 frames
            if frame_count % 30 == 0 and detections:
                print(f"Frame {frame_count}: Detected {len(detections)} objects")
                for det in detections[:3]:  # Show first 3
                    print(f"  - {det['class_name']}: {det['confidence']:.2f}")
            
            frame_count += 1
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print(f"\nProcessed {frame_count} frames")
        print("Demo complete!")


def run_full_demo():
    """Run full demo with all features."""
    print("\n" + "="*60)
    print("Full Object Detection Demo (with Tracking & Estimation)")
    print("="*60 + "\n")
    
    # Check webcam
    print("Checking webcam availability...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Webcam not available.")
        cap.release()
        return
    
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    print(f"✓ Webcam found (FPS: {fps})")
    
    # Initialize components
    print("\nInitializing components...")
    
    try:
        detector = ObjectDetector(model_path="yolov8n.pt", conf_threshold=0.5)
        print("✓ Detector initialized")
        
        tracker = ObjectTracker()
        print("✓ Tracker initialized")
        
        speed_estimator = SpeedEstimator(fps=fps)
        print("✓ Speed estimator initialized")
        
        distance_estimator = DistanceEstimator()
        print("✓ Distance estimator initialized")
        
        visualizer = Visualizer()
        print("✓ Visualizer initialized")
    
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        cap.release()
        return
    
    print("\n" + "="*60)
    print("Starting full detection... Press 'Q' to quit")
    print("="*60 + "\n")
    
    frame_count = 0
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detect
            detections = detector.detect(frame)
            
            # Track
            if tracker.enabled:
                detections = tracker.update(detections, frame_count)
            
            # Estimate distance
            detections = distance_estimator.estimate_distance(detections)
            
            # Estimate speed
            detections = speed_estimator.estimate_speed(detections, frame_count)
            
            # Visualize
            annotated_frame = visualizer.draw_detections(frame, detections)
            
            # Display
            cv2.imshow('Full Object Detection Demo', annotated_frame)
            
            # Print info
            if frame_count % 30 == 0 and detections:
                print(f"\nFrame {frame_count}:")
                for det in detections[:2]:
                    info = f"  - {det['class_name']}"
                    if 'track_id' in det:
                        info += f" (ID: {det['track_id']})"
                    if det.get('distance_m'):
                        info += f" | Distance: {det['distance_m']}m"
                    if det.get('speed_kmh'):
                        info += f" | Speed: {det['speed_kmh']} km/h"
                    print(info)
            
            frame_count += 1
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print(f"\nProcessed {frame_count} frames")
        print("Demo complete!")


def main():
    """Main demo entry point."""
    print("Object Detection System - Demo")
    print("\nChoose demo mode:")
    print("1. Simple Detection (basic YOLO detection)")
    print("2. Full Demo (detection + tracking + estimation)")
    print("3. Create Demo Video")
    
    choice = input("\nEnter choice (1/2/3): ").strip()
    
    if choice == '1':
        run_simple_demo()
    elif choice == '2':
        run_full_demo()
    elif choice == '3':
        video_path = create_demo_video()
        print(f"\nDemo video created: {video_path}")
        print(f"Run: python main.py --source {video_path} --mode video --save-output")
    else:
        print("Invalid choice")


if __name__ == '__main__':
    main()
