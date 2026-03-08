"""
Alert System Module
Handles detection and logging of various alerts like overspeeding.
"""

import logging
import time
from typing import Dict, List, Optional


class AlertSystem:
    """
    Manages and triggers alerts based on detection data and configuration.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize the alert system.
        
        Args:
            config: Alert configuration dictionary
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.enabled = config.get('enabled', False)
        
        self.speed_limit = config.get('speed_limit_kmh', 60)
        self.alert_classes = config.get('alert_classes', ['car', 'truck', 'bus'])
        self.log_alerts = config.get('log_alerts', True)
        
        # Track IDs that have already triggered a specific alert to prevent spam
        self.alerted_tracks = {
            'speed': set()
        }
        
        if self.enabled:
            self.logger.info(f"Alert system enabled: Speed limit {self.speed_limit} km/h")
    
    def check_alerts(self, detections: List[Dict]) -> List[Dict]:
        """
        Check for alerts in current detections.
        
        Args:
            detections: List of detection dictionaries
            
        Returns:
            Updated list of detections with 'alerts' field containing triggered alerts
        """
        if not self.enabled:
            return detections
            
        for det in detections:
            det_alerts = []
            class_name = det.get('class_name')
            track_id = det.get('track_id')
            
            if class_name in self.alert_classes:
                # Check speed alert
                speed_kmh = det.get('speed_kmh')
                if speed_kmh is not None and speed_kmh > self.speed_limit:
                    alert_msg = f"Overspeeding {class_name} ({speed_kmh} km/h)"
                    det_alerts.append({
                        'type': 'speed',
                        'message': alert_msg,
                        'level': 'warning'
                    })
                    det['alert'] = True
                    
                    # Log if it's a new tracked object or we don't have track_id
                    if self.log_alerts:
                        if track_id is None or track_id not in self.alerted_tracks['speed']:
                            self.logger.warning(f"ALERT: {alert_msg}")
                            if track_id is not None:
                                self.alerted_tracks['speed'].add(track_id)
            
            if det_alerts:
                det['alerts_list'] = det_alerts
                
        return detections
