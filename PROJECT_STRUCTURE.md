# Project Structure

```
object_detection/
│
├── config/                          # Configuration files
│   ├── __init__.py
│   ├── config.yaml                  # Main configuration
│   └── camera_calibration.yaml      # Camera calibration parameters
│
├── models/                          # Detection and tracking models
│   ├── __init__.py
│   ├── detector.py                  # YOLO detector wrapper
│   └── tracker.py                   # ByteTrack object tracker
│
├── estimators/                      # Estimation algorithms
│   ├── __init__.py
│   ├── speed_estimator.py          # Vehicle speed estimation
│   ├── height_estimator.py         # Person height estimation
│   ├── distance_estimator.py       # Distance from camera
│   └── direction_detector.py       # Movement direction detection
│
├── utils/                           # Utility modules
│   ├── __init__.py
│   ├── video_handler.py            # Video I/O operations
│   ├── visualization.py            # Drawing and display
│   └── logger.py                   # Data logging (CSV/JSON)
│
├── output/                          # Output directory (auto-created)
│   ├── videos/                     # Annotated videos
│   ├── images/                     # Annotated images
│   ├── data/                       # CSV/JSON exports
│   └── logs/                       # Application logs
│
├── main.py                          # Main application entry point
├── demo.py                          # Interactive demo script
├── test_installation.py             # Installation verification
│
├── requirements.txt                 # Python dependencies
├── .gitignore                      # Git ignore rules
│
├── README.md                        # Project overview
├── QUICKSTART.md                   # Quick start guide
├── MATH_FORMULAS.md                # Mathematical documentation
└── PROJECT_STRUCTURE.md            # This file
```

## Module Descriptions

### Configuration (`config/`)

#### `config.yaml`
Main configuration file containing:
- Detection parameters (model, thresholds, device)
- Tracking parameters (ByteTrack settings)
- Estimation parameters (speed, height, distance)
- Visualization settings
- Output configuration
- Alert system settings

#### `camera_calibration.yaml`
Camera-specific calibration:
- Intrinsic parameters (focal length, principal point)
- Distortion coefficients
- Physical properties (sensor size)
- Mounting parameters (height, angle)
- Perspective transformation points

### Models (`models/`)

#### `detector.py` - ObjectDetector
**Purpose**: Wrapper for YOLOv8 object detection

**Key Features**:
- Single and batch detection
- Configurable confidence/IOU thresholds
- Class filtering
- GPU/CPU support

**Main Methods**:
- `detect(frame)`: Detect objects in single frame
- `detect_batch(frames)`: Batch detection
- `get_class_id(name)`: Get class ID from name

#### `tracker.py` - ObjectTracker
**Purpose**: Multi-object tracking using ByteTrack

**Key Features**:
- Maintains unique IDs across frames
- Trajectory history storage
- Re-identification after occlusion
- Configurable tracking parameters

**Main Methods**:
- `update(detections, frame_id)`: Update tracker
- `get_track_history(track_id)`: Get trajectory
- `get_trajectory(track_id)`: Get center points

### Estimators (`estimators/`)

#### `speed_estimator.py` - SpeedEstimator
**Purpose**: Estimate vehicle speed from frame-to-frame displacement

**Algorithm**:
```
Speed (km/h) = (Pixel Displacement × Scale Factor × FPS × 3.6) / 1000
```

**Key Features**:
- Temporal smoothing
- Calibration support
- Vehicle class filtering

**Main Methods**:
- `estimate_speed(tracked_objects, frame_id)`: Estimate speeds
- `update_calibration(distance_m, distance_px)`: Update calibration

#### `height_estimator.py` - HeightEstimator
**Purpose**: Estimate person height from bounding box

**Algorithm**:
```
Height (cm) = (Bbox Height / Reference Bbox Height) × Reference Height
```

**Key Features**:
- Automatic calibration
- Distance-based correction
- Manual calibration support

**Main Methods**:
- `estimate_height(tracked_objects)`: Estimate heights
- `manual_calibrate(bbox_height, actual_height)`: Manual calibration

#### `distance_estimator.py` - DistanceEstimator
**Purpose**: Estimate distance using pinhole camera model

**Algorithm**:
```
Distance (m) = (Known Object Height × Focal Length) / Bbox Height
```

**Key Features**:
- Multiple object type support
- Focal length calibration
- Distance zone classification

**Main Methods**:
- `estimate_distance(tracked_objects)`: Estimate distances
- `calibrate_focal_length(distance, bbox_height, object_height)`: Calibrate

#### `direction_detector.py` - DirectionDetector
**Purpose**: Detect movement direction from trajectory

**Algorithm**:
```
Direction = arctan2(dy, dx) classified into 8 directions
```

**Key Features**:
- 8-way direction classification
- Velocity calculation
- Approaching detection

**Main Methods**:
- `detect_direction(tracked_objects)`: Detect directions
- `get_velocity(track_id, fps)`: Calculate velocity

### Utilities (`utils/`)

#### `video_handler.py` - VideoHandler
**Purpose**: Handle video input/output operations

**Supported Sources**:
- Image files (JPG, PNG)
- Video files (MP4, AVI)
- Webcam (index 0, 1, ...)
- IP cameras (RTSP streams)

**Main Methods**:
- `read_frame()`: Read next frame
- `initialize_writer(path)`: Setup video writer
- `write_frame(frame)`: Write frame to output

#### `visualization.py` - Visualizer
**Purpose**: Draw annotations on frames

**Displays**:
- Bounding boxes with class colors
- Labels (class, ID, confidence)
- Speed, height, distance
- Movement direction
- FPS counter
- Object count

**Main Methods**:
- `draw_detections(frame, detections, fps)`: Draw all annotations
- `draw_zone(frame, points)`: Draw zone polygon

#### `logger.py` - DataLogger
**Purpose**: Export detection data to files

**Output Formats**:
- CSV: Frame-by-frame detection records
- JSON: Structured data with metadata

**Data Fields**:
- Frame ID, timestamp
- Track ID, class name, confidence
- Bounding box coordinates
- Speed, height, distance
- Movement direction

**Main Methods**:
- `log_frame_data(frame_id, detections)`: Log frame
- `get_statistics()`: Calculate statistics
- `close()`: Save and close files

### Main Application (`main.py`)

#### ObjectDetectionApp
**Purpose**: Main application orchestrator

**Responsibilities**:
- Load configuration
- Initialize all components
- Process frames through pipeline
- Handle output and logging

**Processing Pipeline**:
1. Detect objects (YOLO)
2. Track objects (ByteTrack)
3. Estimate distance
4. Estimate speed
5. Estimate height
6. Detect direction
7. Visualize results
8. Log data

**Command-Line Arguments**:
- `--source`: Input source
- `--mode`: Input mode (image/video/webcam/stream)
- `--config`: Configuration file path
- `--save-output`: Save annotated video
- `--export-data`: Export data to CSV/JSON
- `--no-display`: Disable display window

## Data Flow

```
Input Source
    ↓
Video Handler (read frames)
    ↓
Object Detector (YOLO)
    ↓
Object Tracker (ByteTrack)
    ↓
Distance Estimator
    ↓
Speed Estimator
    ↓
Height Estimator
    ↓
Direction Detector
    ↓
Visualizer (draw annotations)
    ↓
Data Logger (export data)
    ↓
Output (video/data files)
```

## Configuration Flow

```
config.yaml
    ↓
ObjectDetectionApp.__init__()
    ↓
Initialize Components:
    - ObjectDetector
    - ObjectTracker
    - SpeedEstimator
    - HeightEstimator
    - DistanceEstimator
    - DirectionDetector
    - Visualizer
    - DataLogger
```

## Extension Points

### Adding New Estimators

1. Create new file in `estimators/`
2. Implement estimation logic
3. Add to `main.py` initialization
4. Add configuration to `config.yaml`
5. Update visualization if needed

### Adding New Object Classes

1. Update `known_object_heights` in `config.yaml`
2. Add color mapping in visualization config
3. Update class filtering if needed

### Custom Alert System

1. Define alert conditions in `config.yaml`
2. Implement alert logic in processing pipeline
3. Add alert logging to data logger

### Integration with External Systems

1. Modify `DataLogger` to send data to API/database
2. Add real-time streaming output
3. Implement webhook notifications

## Performance Considerations

### Optimization Strategies

1. **Model Selection**:
   - YOLOv8n: Fastest (45+ FPS)
   - YOLOv8x: Most accurate (10-15 FPS)

2. **Frame Skipping**:
   - Set `skip_frames` in config
   - Process every Nth frame

3. **Resolution Reduction**:
   - Reduce `imgsz` parameter
   - Resize input frames

4. **GPU Acceleration**:
   - Set `device: cuda` in config
   - Install CUDA-enabled PyTorch

5. **Batch Processing**:
   - Use `detect_batch()` for offline processing
   - Process multiple frames simultaneously

### Memory Management

- Track history limited by `maxlen` in deques
- Periodic cleanup of old tracks
- Configurable buffer sizes

## Testing

### Unit Tests
- Test individual estimators
- Verify mathematical formulas
- Check edge cases

### Integration Tests
- Test full pipeline
- Verify data export
- Check configuration loading

### Performance Tests
- Measure FPS on different hardware
- Profile memory usage
- Benchmark estimation accuracy

## Deployment

### Local Deployment
1. Install dependencies
2. Configure camera parameters
3. Run main application

### Server Deployment
1. Use `--no-display` flag
2. Configure output paths
3. Set up data export pipeline
4. Monitor logs

### Edge Device Deployment
1. Use YOLOv8n model
2. Reduce resolution
3. Optimize for CPU
4. Minimize dependencies

## Maintenance

### Regular Tasks
- Update YOLO models
- Recalibrate camera parameters
- Review and clean output directory
- Monitor log files

### Troubleshooting
- Check logs in `output/logs/`
- Verify configuration
- Test with demo script
- Run installation test

## License

MIT License - See README.md for details
