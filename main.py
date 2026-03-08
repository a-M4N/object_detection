"""
Main Application
Real-time object detection and tracking system with advanced estimation features.
"""

import argparse
import cv2
import yaml
import logging
import sys
import time
from pathlib import Path
from typing import Dict, Optional

from models.detector import ObjectDetector
from models.tracker import ObjectTracker
from estimators.speed_estimator import SpeedEstimator
from estimators.height_estimator import HeightEstimator
from estimators.distance_estimator import DistanceEstimator
from estimators.direction_detector import DirectionDetector
from estimators.ppe_detector import PPEDetector
from utils.video_handler import VideoHandler
from utils.visualization import Visualizer
from utils.logger import DataLogger
from utils.alert_system import AlertSystem


class ObjectDetectionApp:
    """
    Main application class for object detection and tracking.
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize application.
        
        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Setup logging
        self._setup_logging()
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing Object Detection Application")
        
        # Initialize components
        self._initialize_components()
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            print(f"Error loading config: {e}")
            sys.exit(1)
    
    def _setup_logging(self):
        """Setup logging configuration."""
        log_config = self.config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        
        # Create logs directory
        if log_config.get('log_to_file', True):
            log_file = log_config.get('log_file', 'output/logs/app.log')
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
            
            logging.basicConfig(
                level=log_level,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(log_file),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        else:
            logging.basicConfig(
                level=log_level,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[logging.StreamHandler(sys.stdout)]
            )
    
    def _initialize_components(self):
        """Initialize all system components."""
        # Detector
        det_config = self.config['detection']
        self.detector = ObjectDetector(
            model_path=det_config['model'],
            conf_threshold=det_config['confidence_threshold'],
            iou_threshold=det_config['iou_threshold'],
            device=det_config['device'],
            imgsz=det_config['imgsz']
        )
        
        # Tracker
        if self.config['tracking']['enabled']:
            track_config = self.config['tracking']
            self.tracker = ObjectTracker(
                track_thresh=track_config['track_thresh'],
                track_buffer=track_config['track_buffer'],
                match_thresh=track_config['match_thresh'],
                min_box_area=track_config['min_box_area']
            )
        else:
            self.tracker = None
        
        # Speed Estimator
        if self.config['speed_estimation']['enabled']:
            speed_config = self.config['speed_estimation']
            self.speed_estimator = SpeedEstimator(
                reference_distance_meters=speed_config['reference_distance_meters'],
                reference_distance_pixels=speed_config['reference_distance_pixels'],
                fps=speed_config.get('fps', 30),
                smoothing_window=speed_config['smoothing_window'],
                vehicle_classes=speed_config['vehicle_classes']
            )
        else:
            self.speed_estimator = None
        
        # Height Estimator
        if self.config['height_estimation']['enabled']:
            height_config = self.config['height_estimation']
            self.height_estimator = HeightEstimator(
                average_person_height_cm=height_config['average_person_height_cm'],
                camera_height_cm=height_config['camera_height_cm'],
                camera_angle_deg=height_config['camera_angle_deg']
            )
        else:
            self.height_estimator = None
        
        # Distance Estimator
        if self.config['distance_estimation']['enabled']:
            dist_config = self.config['distance_estimation']
            self.distance_estimator = DistanceEstimator(
                focal_length_pixels=dist_config['focal_length_pixels'],
                known_object_heights=dist_config['known_object_heights']
            )
        else:
            self.distance_estimator = None
        
        # Direction Detector
        if self.config['direction_detection']['enabled']:
            dir_config = self.config['direction_detection']
            self.direction_detector = DirectionDetector(
                min_displacement=dir_config['min_displacement'],
                history_frames=dir_config['history_frames']
            )
        else:
            self.direction_detector = None
            
        # PPE Detector
        if self.config.get('ppe_detection', {}).get('enabled', False):
            ppe_config = self.config['ppe_detection']
            self.ppe_detector = PPEDetector(
                model_path=ppe_config.get('model', 'yolov8n.pt'),
                conf_threshold=ppe_config.get('confidence_threshold', 0.5),
                iou_threshold=ppe_config.get('iou_threshold', 0.45),
                device=self.config['detection']['device'],
                required_items=ppe_config.get('required_items', [])
            )
        else:
            self.ppe_detector = None
        
        # Alert System
        alerts_config = self.config.get('alerts', {})
        self.alert_system = AlertSystem(alerts_config)
        
        # Visualizer
        vis_config = self.config['visualization']
        self.visualizer = Visualizer(
            show_bbox=vis_config['show_bbox'],
            show_label=vis_config['show_label'],
            show_confidence=vis_config['show_confidence'],
            show_track_id=vis_config['show_track_id'],
            show_speed=vis_config['show_speed'],
            show_height=vis_config['show_height'],
            show_distance=vis_config['show_distance'],
            show_direction=vis_config['show_direction'],
            show_fps=vis_config['show_fps'],
            bbox_thickness=vis_config['bbox_thickness'],
            font_scale=vis_config['font_scale'],
            font_thickness=vis_config['font_thickness'],
            colors=vis_config.get('colors')
        )
        
        self.logger.info("All components initialized successfully")
    
    def process_frame(self, frame, frame_id: int):
        """
        Process a single frame.
        
        Args:
            frame: Input frame
            frame_id: Frame number
        
        Returns:
            Tuple of (annotated_frame, detections)
        """
        # Detect objects
        detections = self.detector.detect(frame)
        
        # Track objects
        if self.tracker is not None and self.tracker.enabled:
            detections = self.tracker.update(detections, frame_id)
        
        # Estimate distance
        if self.distance_estimator is not None:
            detections = self.distance_estimator.estimate_distance(detections)
        
        # Estimate speed
        if self.speed_estimator is not None:
            detections = self.speed_estimator.estimate_speed(detections, frame_id)
        
        # Estimate height
        if self.height_estimator is not None:
            detections = self.height_estimator.estimate_height(
                detections,
                self.distance_estimator
            )
        
        # Detect direction
        if self.direction_detector is not None:
            detections = self.direction_detector.detect_direction(detections)
            
        # Detect PPE
        if getattr(self, 'ppe_detector', None) is not None:
            detections = self.ppe_detector.check_ppe(frame, detections)
        
        # Check alerts
        if self.alert_system is not None:
            detections = self.alert_system.check_alerts(detections)
        
        return detections
    
    def run(
        self,
        source: str,
        mode: str = 'video',
        save_output: bool = False,
        export_data: bool = False,
        show_display: bool = True
    ):
        """
        Run object detection on input source.
        
        Args:
            source: Input source (file path, webcam index, or RTSP URL)
            mode: Input mode ('image', 'video', 'webcam', 'stream')
            save_output: Save annotated video
            export_data: Export detection data
            show_display: Show live display window
        """
        self.logger.info(f"Starting processing: mode={mode}, source={source}")
        
        # Initialize video handler
        video_handler = VideoHandler(source, mode)
        
        # Update FPS in speed estimator
        if self.speed_estimator is not None:
            self.speed_estimator.update_fps(video_handler.fps)
        
        # Initialize output
        output_config = self.config['output']
        output_dir = Path(output_config['output_dir'])
        
        # Video writer
        if save_output and mode != 'image':
            output_video_path = output_dir / 'videos' / f'output_{int(time.time())}.mp4'
            output_video_path.parent.mkdir(parents=True, exist_ok=True)
            video_handler.initialize_writer(
                str(output_video_path),
                codec=output_config['video_codec'],
                fps=output_config['video_fps']
            )
            self.logger.info(f"Output video: {output_video_path}")
        
        # Data logger
        data_logger = None
        if export_data:
            data_format = output_config['data_format']
            data_logger = DataLogger(
                output_dir=str(output_dir / 'data'),
                save_csv=data_format in ['csv', 'both'],
                save_json=data_format in ['json', 'both']
            )
            data_logger.initialize_csv()
        
        # Process frames
        frame_id = 0
        fps_start_time = time.time()
        fps_frame_count = 0
        current_fps = 0.0
        
        try:
            if mode == 'image':
                # Process single image
                frame = video_handler.read_image()
                if frame is not None:
                    detections = self.process_frame(frame, frame_id)
                    annotated_frame = self.visualizer.draw_detections(frame, detections)
                    
                    # Save output
                    if save_output:
                        output_image_path = output_dir / 'images' / f'output_{int(time.time())}.jpg'
                        output_image_path.parent.mkdir(parents=True, exist_ok=True)
                        cv2.imwrite(str(output_image_path), annotated_frame)
                        self.logger.info(f"Output image saved: {output_image_path}")
                    
                    # Show display
                    if show_display:
                        cv2.imshow('Object Detection', annotated_frame)
                        cv2.waitKey(0)
                        cv2.destroyAllWindows()
                    
                    # Export data
                    if data_logger is not None:
                        data_logger.log_frame_data(frame_id, detections)
            
            else:
                # Process video/webcam/stream
                while True:
                    ret, frame = video_handler.read_frame()
                    if not ret:
                        break
                    
                    # Process frame
                    detections = self.process_frame(frame, frame_id)
                    
                    # Calculate FPS
                    fps_frame_count += 1
                    if fps_frame_count >= 30:
                        elapsed_time = time.time() - fps_start_time
                        current_fps = fps_frame_count / elapsed_time
                        fps_start_time = time.time()
                        fps_frame_count = 0
                    
                    # Visualize
                    annotated_frame = self.visualizer.draw_detections(
                        frame,
                        detections,
                        fps=current_fps
                    )
                    
                    # Save output
                    if save_output:
                        video_handler.write_frame(annotated_frame)
                    
                    # Show display
                    if show_display:
                        cv2.imshow('Object Detection', annotated_frame)
                        key = cv2.waitKey(1) & 0xFF
                        if key == ord('q'):
                            self.logger.info("User requested quit")
                            break
                    
                    # Export data
                    if data_logger is not None:
                        data_logger.log_frame_data(
                            frame_id,
                            detections,
                            frame_id / video_handler.fps
                        )
                    
                    frame_id += 1
                    
                    # Log progress
                    if frame_id % 100 == 0:
                        progress = video_handler.get_progress()
                        self.logger.info(f"Processed {frame_id} frames ({progress:.1f}%)")
        
        except KeyboardInterrupt:
            self.logger.info("Processing interrupted by user")
        
        except Exception as e:
            self.logger.error(f"Error during processing: {e}", exc_info=True)
        
        finally:
            # Cleanup
            video_handler.release()
            cv2.destroyAllWindows()
            
            if data_logger is not None:
                data_logger.close()
                stats = data_logger.get_statistics()
                self.logger.info(f"Statistics: {stats}")
            
            self.logger.info(f"Processing complete: {frame_id} frames processed")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Real-time Object Detection and Tracking System'
    )
    
    parser.add_argument(
        '--source',
        type=str,
        required=True,
        help='Input source (image/video file, webcam index, or RTSP URL)'
    )
    
    parser.add_argument(
        '--mode',
        type=str,
        choices=['image', 'video', 'webcam', 'stream'],
        default='video',
        help='Input mode'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config/config.yaml',
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--save-output',
        action='store_true',
        help='Save annotated output'
    )
    
    parser.add_argument(
        '--export-data',
        action='store_true',
        help='Export detection data to CSV/JSON'
    )
    
    parser.add_argument(
        '--no-display',
        action='store_true',
        help='Disable live display window'
    )
    
    args = parser.parse_args()
    
    # Create and run application
    app = ObjectDetectionApp(config_path=args.config)
    app.run(
        source=args.source,
        mode=args.mode,
        save_output=args.save_output,
        export_data=args.export_data,
        show_display=not args.no_display
    )


if __name__ == '__main__':
    main()
