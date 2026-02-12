# Real-Time Object Detection & Tracking System

A comprehensive Python-based object detection application using YOLOv8 with advanced tracking, speed estimation, height estimation, and distance calculation capabilities.

## Features

### Core Detection
- **YOLOv8** (latest YOLO version) for high-accuracy real-time object detection
- Support for 80+ COCO object classes (person, car, bike, truck, bus, animals, etc.)
- Multiple input sources:
  - Image files (JPG, PNG, etc.)
  - Video files (MP4, AVI, etc.)
  - Webcam (live camera feed)
  - IP camera streams (RTSP)

### Object Tracking
- **ByteTrack** integration for robust multi-object tracking
- Maintains unique IDs across frames
- Handles occlusions and re-identification
- Smooth trajectory tracking

### Advanced Estimation Features

#### 1. Vehicle Speed Estimation
- Real-world speed calculation (km/h)
- Frame-to-frame displacement tracking
- Perspective transformation support
- Configurable reference distance scaling
- Camera calibration parameters

**Mathematical Formula:**
```
Speed (km/h) = (Pixel Displacement × Scale Factor × FPS × 3.6) / 1000
where Scale Factor = Real World Distance / Pixel Distance
```

#### 2. Person Height Estimation
- Human height estimation using bounding box analysis
- Camera focal length and depth approximation
- Reference height calibration

**Mathematical Formula:**
```
Height (cm) = (Bbox Height × Real Distance × Sensor Height) / (Focal Length × Image Height)
```

#### 3. Distance from Camera
- Approximate distance calculation for each detected object
- Based on bounding box size and known object dimensions

**Mathematical Formula:**
```
Distance (m) = (Known Object Height × Focal Length) / Bbox Height in Pixels
```

#### 4. Movement Direction Detection
- Tracks object movement (left/right/forward/backward)
- Velocity vector analysis
- Trajectory prediction

### Real-Time Visualization
- Bounding boxes with color-coded labels
- Unique tracking IDs
- Speed display (for vehicles)
- Height display (for persons)
- Distance from camera
- Movement direction indicators
- FPS and performance metrics
- Confidence scores

### Output & Logging
- Save annotated video output
- Export detection data to CSV/JSON
- Frame-by-frame tracking logs
- Optional alert system for custom conditions (e.g., overspeed detection)

## System Architecture

```
object_detection/
├── config/
│   ├── __init__.py
│   ├── config.yaml           # Main configuration file
│   └── camera_calibration.yaml
├── models/
│   ├── __init__.py
│   ├── detector.py           # YOLO detection wrapper
│   └── tracker.py            # ByteTrack integration
├── estimators/
│   ├── __init__.py
│   ├── speed_estimator.py    # Vehicle speed estimation
│   ├── height_estimator.py   # Person height estimation
│   ├── distance_estimator.py # Distance calculation
│   └── direction_detector.py # Movement direction
├── utils/
│   ├── __init__.py
│   ├── video_handler.py      # Video I/O operations
│   ├── visualization.py      # Drawing and display
│   ├── calibration.py        # Camera calibration
│   └── logger.py             # Data logging
├── main.py                   # Main application entry point
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Installation

### Prerequisites
- Python 3.8 or higher
- CUDA-capable GPU (recommended for real-time performance)
- Webcam or IP camera (for live streaming)

### Step 1: Clone or Navigate to Project Directory
```bash
cd c:\Users\ASUS\OneDrive\Documents\object_detection
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Download YOLO Model
The YOLOv8 model will be automatically downloaded on first run. You can also manually download:
```bash
# Models will be cached in ~/.ultralytics/
```

## Configuration

Edit `config/config.yaml` to customize:
- Model selection (yolov8n, yolov8s, yolov8m, yolov8l, yolov8x)
- Confidence threshold
- IOU threshold
- Tracking parameters
- Camera calibration parameters
- Speed/height estimation settings
- Alert conditions

### Camera Calibration
For accurate measurements, calibrate your camera:
1. Edit `config/camera_calibration.yaml`
2. Set focal length, sensor size, and reference distances
3. Optionally perform full calibration using checkerboard pattern

## Usage

### 1. Process Image File
```bash
python main.py --source path/to/image.jpg --mode image
```

### 2. Process Video File
```bash
python main.py --source path/to/video.mp4 --mode video --save-output
```

### 3. Webcam (Live Camera)
```bash
python main.py --source 0 --mode webcam
```

### 4. IP Camera Stream
```bash
python main.py --source rtsp://username:password@ip:port/stream --mode stream
```

### 5. Advanced Options
```bash
python main.py \
  --source video.mp4 \
  --mode video \
  --model yolov8m \
  --conf 0.5 \
  --save-output \
  --export-data \
  --enable-alerts \
  --speed-threshold 80
```

### Command-Line Arguments
- `--source`: Input source (file path, 0 for webcam, RTSP URL)
- `--mode`: Input mode (image/video/webcam/stream)
- `--model`: YOLO model variant (yolov8n/s/m/l/x)
- `--conf`: Confidence threshold (0.0-1.0)
- `--iou`: IOU threshold for NMS (0.0-1.0)
- `--save-output`: Save annotated video
- `--export-data`: Export detection data to CSV/JSON
- `--enable-alerts`: Enable alert system
- `--speed-threshold`: Speed limit for alerts (km/h)
- `--output-dir`: Output directory for results

## Output Files

### Video Output
- Location: `output/videos/`
- Format: MP4 with H264 codec
- Contains: Annotated frames with all visualizations

### Data Export
- Location: `output/data/`
- Formats: CSV and JSON
- Contains:
  - Frame number
  - Object ID
  - Class name
  - Bounding box coordinates
  - Confidence score
  - Speed (if vehicle)
  - Height (if person)
  - Distance from camera
  - Movement direction

### Logs
- Location: `output/logs/`
- Contains: System logs, alerts, and performance metrics

## Performance Optimization

### Model Selection
- **YOLOv8n**: Fastest, lowest accuracy (~45 FPS on GPU)
- **YOLOv8s**: Balanced (~35 FPS on GPU)
- **YOLOv8m**: Good accuracy (~25 FPS on GPU)
- **YOLOv8l**: High accuracy (~15 FPS on GPU)
- **YOLOv8x**: Highest accuracy (~10 FPS on GPU)

### Hardware Recommendations
- **CPU Only**: YOLOv8n, 5-10 FPS
- **GPU (GTX 1060+)**: YOLOv8s/m, 20-35 FPS
- **GPU (RTX 3060+)**: YOLOv8l/x, 15-45 FPS

### Optimization Tips
1. Use smaller model for real-time performance
2. Reduce input resolution (e.g., 640x640 → 416x416)
3. Increase confidence threshold to reduce detections
4. Use GPU acceleration (CUDA)
5. Disable unnecessary estimation modules

## Mathematical Formulas Explained

### 1. Speed Estimation
```
Given:
- p1, p2: Object positions in consecutive frames (pixels)
- fps: Frames per second
- scale: Pixels to meters conversion factor

Displacement (pixels) = sqrt((p2.x - p1.x)² + (p2.y - p1.y)²)
Displacement (meters) = Displacement (pixels) × scale
Speed (m/s) = Displacement (meters) × fps
Speed (km/h) = Speed (m/s) × 3.6
```

### 2. Height Estimation
```
Given:
- bbox_height: Bounding box height (pixels)
- distance: Distance from camera (meters)
- focal_length: Camera focal length (pixels)
- sensor_height: Camera sensor height (mm)
- image_height: Image height (pixels)

Height (m) = (bbox_height × distance × sensor_height) / (focal_length × image_height)
```

### 3. Distance Estimation
```
Given:
- known_height: Known real-world object height (meters)
- bbox_height: Bounding box height (pixels)
- focal_length: Camera focal length (pixels)

Distance (m) = (known_height × focal_length) / bbox_height
```

### 4. Perspective Transformation
For accurate speed estimation on roads:
```
- Define 4 reference points in image (trapezoid)
- Map to real-world rectangle coordinates
- Apply homography transformation
- Calculate distances in bird's-eye view
```

## Alert System

Configure custom alerts in `config/config.yaml`:
```yaml
alerts:
  enabled: true
  conditions:
    - type: speed
      threshold: 80  # km/h
      classes: [car, truck, bus]
    - type: intrusion
      zone: [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
      classes: [person]
```

## Troubleshooting

### Low FPS
- Use smaller YOLO model (yolov8n)
- Reduce input resolution
- Disable estimation modules
- Check GPU availability

### Inaccurate Speed/Height
- Calibrate camera properly
- Set correct reference distances
- Adjust scale factors
- Use perspective transformation

### Tracking Issues
- Increase IOU threshold
- Adjust tracking parameters
- Improve lighting conditions
- Reduce motion blur

## Dependencies

- **ultralytics**: YOLOv8 implementation
- **opencv-python**: Video processing and visualization
- **numpy**: Numerical computations
- **pandas**: Data export
- **pyyaml**: Configuration management
- **supervision**: ByteTrack integration

## License

MIT License - Feel free to use and modify for your projects.

## Contributing

Contributions are welcome! Please submit pull requests or open issues for bugs and feature requests.

## References

- [YOLOv8 Documentation](https://docs.ultralytics.com/)
- [ByteTrack Paper](https://arxiv.org/abs/2110.06864)
- [OpenCV Documentation](https://docs.opencv.org/)

## Author

Created for real-world computer vision applications with focus on accuracy, efficiency, and scalability.
