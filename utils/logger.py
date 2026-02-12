"""
Data Logger
Handles logging detection data to CSV and JSON formats.
"""

import csv
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class DataLogger:
    """
    Logs detection and tracking data to files.
    """
    
    def __init__(
        self,
        output_dir: str = "output/data",
        save_csv: bool = True,
        save_json: bool = True
    ):
        """
        Initialize data logger.
        
        Args:
            output_dir: Directory to save data files
            save_csv: Save data in CSV format
            save_json: Save data in JSON format
        """
        self.logger = logging.getLogger(__name__)
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.save_csv = save_csv
        self.save_json = save_json
        
        # Data storage
        self.data_records = []
        
        # CSV file handle
        self.csv_file = None
        self.csv_writer = None
        
        # Generate timestamp for filenames
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        self.logger.info(f"Data logger initialized: {self.output_dir}")
    
    def initialize_csv(self):
        """Initialize CSV file and writer."""
        if not self.save_csv:
            return
        
        csv_path = self.output_dir / f"detections_{self.timestamp}.csv"
        
        try:
            self.csv_file = open(csv_path, 'w', newline='', encoding='utf-8')
            
            # Define CSV columns
            fieldnames = [
                'frame_id',
                'timestamp',
                'track_id',
                'class_name',
                'confidence',
                'bbox_x1',
                'bbox_y1',
                'bbox_x2',
                'bbox_y2',
                'center_x',
                'center_y',
                'speed_kmh',
                'height_cm',
                'distance_m',
                'direction',
                'movement_x',
                'movement_y'
            ]
            
            self.csv_writer = csv.DictWriter(self.csv_file, fieldnames=fieldnames)
            self.csv_writer.writeheader()
            
            self.logger.info(f"CSV file initialized: {csv_path}")
        
        except Exception as e:
            self.logger.error(f"Failed to initialize CSV file: {e}")
    
    def log_frame_data(
        self,
        frame_id: int,
        detections: List[Dict],
        timestamp: Optional[float] = None
    ):
        """
        Log detection data for a frame.
        
        Args:
            frame_id: Frame number
            detections: List of detections
            timestamp: Optional timestamp in seconds
        """
        if timestamp is None:
            timestamp = frame_id / 30.0  # Assume 30 FPS
        
        for det in detections:
            record = self._create_record(frame_id, timestamp, det)
            
            # Add to in-memory storage
            self.data_records.append(record)
            
            # Write to CSV
            if self.csv_writer is not None:
                self.csv_writer.writerow(record)
    
    def _create_record(
        self,
        frame_id: int,
        timestamp: float,
        detection: Dict
    ) -> Dict:
        """
        Create a data record from detection.
        
        Args:
            frame_id: Frame number
            timestamp: Timestamp in seconds
            detection: Detection dictionary
        
        Returns:
            Data record dictionary
        """
        bbox = detection.get('bbox', [0, 0, 0, 0])
        center = detection.get('center', (0, 0))
        movement = detection.get('movement_vector', (0, 0))
        
        record = {
            'frame_id': frame_id,
            'timestamp': round(timestamp, 3),
            'track_id': detection.get('track_id', -1),
            'class_name': detection.get('class_name', 'unknown'),
            'confidence': round(detection.get('confidence', 0), 3),
            'bbox_x1': round(bbox[0], 2),
            'bbox_y1': round(bbox[1], 2),
            'bbox_x2': round(bbox[2], 2),
            'bbox_y2': round(bbox[3], 2),
            'center_x': round(center[0], 2),
            'center_y': round(center[1], 2),
            'speed_kmh': detection.get('speed_kmh'),
            'height_cm': detection.get('height_cm'),
            'distance_m': detection.get('distance_m'),
            'direction': detection.get('direction', 'Unknown'),
            'movement_x': round(movement[0], 2) if movement else 0,
            'movement_y': round(movement[1], 2) if movement else 0
        }
        
        return record
    
    def save_json(self):
        """Save all data to JSON file."""
        if not self.save_json or len(self.data_records) == 0:
            return
        
        json_path = self.output_dir / f"detections_{self.timestamp}.json"
        
        try:
            # Group records by frame
            frames_data = {}
            for record in self.data_records:
                frame_id = record['frame_id']
                if frame_id not in frames_data:
                    frames_data[frame_id] = {
                        'frame_id': frame_id,
                        'timestamp': record['timestamp'],
                        'detections': []
                    }
                
                # Remove frame_id and timestamp from detection record
                det_record = {k: v for k, v in record.items() 
                             if k not in ['frame_id', 'timestamp']}
                frames_data[frame_id]['detections'].append(det_record)
            
            # Convert to list and sort by frame_id
            output_data = {
                'metadata': {
                    'total_frames': len(frames_data),
                    'total_detections': len(self.data_records),
                    'generated_at': self.timestamp
                },
                'frames': sorted(frames_data.values(), key=lambda x: x['frame_id'])
            }
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2)
            
            self.logger.info(f"JSON file saved: {json_path}")
        
        except Exception as e:
            self.logger.error(f"Failed to save JSON file: {e}")
    
    def get_statistics(self) -> Dict:
        """
        Get statistics from logged data.
        
        Returns:
            Dictionary of statistics
        """
        if len(self.data_records) == 0:
            return {}
        
        # Count detections by class
        class_counts = {}
        track_ids = set()
        speeds = []
        heights = []
        distances = []
        
        for record in self.data_records:
            class_name = record['class_name']
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
            
            if record['track_id'] != -1:
                track_ids.add(record['track_id'])
            
            if record['speed_kmh'] is not None:
                speeds.append(record['speed_kmh'])
            
            if record['height_cm'] is not None:
                heights.append(record['height_cm'])
            
            if record['distance_m'] is not None:
                distances.append(record['distance_m'])
        
        stats = {
            'total_detections': len(self.data_records),
            'unique_tracks': len(track_ids),
            'class_counts': class_counts,
            'speed_stats': {
                'avg': round(sum(speeds) / len(speeds), 2) if speeds else 0,
                'max': round(max(speeds), 2) if speeds else 0,
                'min': round(min(speeds), 2) if speeds else 0
            } if speeds else None,
            'height_stats': {
                'avg': round(sum(heights) / len(heights), 2) if heights else 0,
                'max': round(max(heights), 2) if heights else 0,
                'min': round(min(heights), 2) if heights else 0
            } if heights else None,
            'distance_stats': {
                'avg': round(sum(distances) / len(distances), 2) if distances else 0,
                'max': round(max(distances), 2) if distances else 0,
                'min': round(min(distances), 2) if distances else 0
            } if distances else None
        }
        
        return stats
    
    def close(self):
        """Close logger and save final data."""
        # Close CSV file
        if self.csv_file is not None:
            self.csv_file.close()
            self.logger.info("CSV file closed")
        
        # Save JSON
        self.save_json()
        
        # Log statistics
        stats = self.get_statistics()
        if stats:
            self.logger.info(f"Data logging complete: {stats['total_detections']} detections, "
                           f"{stats['unique_tracks']} unique tracks")
