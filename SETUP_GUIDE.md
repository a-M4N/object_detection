# Complete Setup and Usage Guide

## 🎯 Project Overview

This is a **production-ready, real-time object detection and tracking system** built with:
- **YOLOv8** (latest YOLO version) for object detection
- **ByteTrack** for multi-object tracking
- **Advanced estimation algorithms** for speed, height, distance, and direction
- **Modular architecture** for easy customization and extension

---

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Usage Examples](#usage-examples)
5. [Configuration](#configuration)
6. [Output Files](#output-files)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Features](#advanced-features)

---

## 💻 System Requirements

### Minimum Requirements
- **OS**: Windows 10/11, Linux, macOS
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space

### Recommended for Real-Time Performance
- **GPU**: NVIDIA GPU with CUDA support (GTX 1060 or better)
- **RAM**: 16GB
- **CPU**: Intel i5 or AMD Ryzen 5 (or better)

### Supported Input Sources
- ✅ Image files (JPG, PNG, BMP)
- ✅ Video files (MP4, AVI, MOV)
- ✅ Webcam (USB or built-in)
- ✅ IP cameras (RTSP streams)

---

## 🚀 Installation

### Step 1: Navigate to Project Directory
```bash
cd c:\Users\ASUS\OneDrive\Documents\object_detection
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
```

### Step 3: Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### Step 4: Upgrade pip
```bash
python -m pip install --upgrade pip
```

### Step 5: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 6: (Optional) Install CUDA-enabled PyTorch

For GPU acceleration:
```bash
# For CUDA 11.8
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

### Step 7: Verify Installation
```bash
python test_installation.py
```

Expected output:
```
✓ ultralytics installed
✓ opencv-python installed
✓ supervision installed
✓ YOLO model loaded successfully
✓ All critical tests passed!
```

---

## ⚡ Quick Start

### 1. Test with Webcam (Simplest)
```bash
python main.py --source 0 --mode webcam
```

Press **Q** to quit.

### 2. Process a Video File
```bash
python main.py --source path/to/video.mp4 --mode video --save-output --export-data
```

### 3. Process an Image
```bash
python main.py --source path/to/image.jpg --mode image --save-output
```

### 4. Run Interactive Demo
```bash
python demo.py
```

---

## 📚 Usage Examples

### Example 1: Basic Detection (Webcam)
```bash
python main.py --source 0 --mode webcam
```

**What it does:**
- Opens webcam
- Detects objects in real-time
- Shows live display with bounding boxes
- Displays FPS

### Example 2: Full Pipeline (Video File)
```bash
python main.py \
  --source traffic_video.mp4 \
  --mode video \
  --save-output \
  --export-data
```

**What it does:**
- Processes video file
- Detects and tracks objects
- Estimates speed, height, distance, direction
- Saves annotated video to `output/videos/`
- Exports data to `output/data/` (CSV + JSON)

### Example 3: IP Camera Stream
```bash
python main.py \
  --source "rtsp://username:password@192.168.1.100:554/stream" \
  --mode stream \
  --save-output
```

**What it does:**
- Connects to IP camera
- Processes live stream
- Saves annotated video

### Example 4: Headless Processing (No Display)
```bash
python main.py \
  --source video.mp4 \
  --mode video \
  --save-output \
  --export-data \
  --no-display
```

**What it does:**
- Processes video without showing display window
- Useful for server/batch processing
- Saves all outputs to files

### Example 5: Custom Configuration
```bash
python main.py \
  --source video.mp4 \
  --mode video \
  --config config/custom_config.yaml \
  --save-output
```

---

## ⚙️ Configuration

### Main Configuration File: `config/config.yaml`

#### Detection Settings
```yaml
detection:
  model: "yolov8m.pt"              # Model: yolov8n/s/m/l/x
  confidence_threshold: 0.5        # Min confidence (0.0-1.0)
  iou_threshold: 0.45              # IOU for NMS
  device: "cuda"                   # cuda or cpu
  imgsz: 640                       # Input size
```

**Model Selection Guide:**
- `yolov8n`: Fastest, lowest accuracy (~45 FPS on GPU)
- `yolov8s`: Balanced (~35 FPS)
- `yolov8m`: Good accuracy (~25 FPS) ⭐ **Recommended**
- `yolov8l`: High accuracy (~15 FPS)
- `yolov8x`: Highest accuracy (~10 FPS)

#### Speed Estimation
```yaml
speed_estimation:
  enabled: true
  reference_distance_meters: 10.0   # Known real-world distance
  reference_distance_pixels: 200    # Corresponding pixel distance
  fps: 30                           # Video FPS
  smoothing_window: 5               # Frames to average
```

**Calibration:**
1. Measure a known distance in your scene (e.g., 10 meters)
2. Count the pixel distance in a frame
3. Update the values above

#### Visualization
```yaml
visualization:
  show_bbox: true          # Bounding boxes
  show_label: true         # Class names
  show_track_id: true      # Tracking IDs
  show_speed: true         # Speed (for vehicles)
  show_height: true        # Height (for persons)
  show_distance: true      # Distance from camera
  show_direction: true     # Movement direction
  show_fps: true           # FPS counter
```

### Camera Calibration: `config/camera_calibration.yaml`

```yaml
camera_matrix:
  fx: 700.0    # Focal length X
  fy: 700.0    # Focal length Y
  cx: 640.0    # Principal point X
  cy: 360.0    # Principal point Y

camera_properties:
  sensor_width_mm: 6.17
  sensor_height_mm: 4.55
  focal_length_mm: 3.6
```

---

## 📁 Output Files

### Directory Structure
```
output/
├── videos/
│   └── output_<timestamp>.mp4      # Annotated video
├── images/
│   └── output_<timestamp>.jpg      # Annotated image
├── data/
│   ├── detections_<timestamp>.csv  # CSV export
│   └── detections_<timestamp>.json # JSON export
└── logs/
    └── app.log                     # Application logs
```

### CSV Format
```csv
frame_id,timestamp,track_id,class_name,confidence,bbox_x1,bbox_y1,bbox_x2,bbox_y2,speed_kmh,height_cm,distance_m,direction
0,0.000,1,car,0.95,100,200,300,400,45.2,NULL,15.3,Right
1,0.033,1,car,0.96,105,200,305,400,46.1,NULL,15.1,Right
```

### JSON Format
```json
{
  "metadata": {
    "total_frames": 300,
    "total_detections": 1250
  },
  "frames": [
    {
      "frame_id": 0,
      "timestamp": 0.000,
      "detections": [
        {
          "track_id": 1,
          "class_name": "car",
          "confidence": 0.95,
          "bbox_x1": 100,
          "speed_kmh": 45.2,
          "distance_m": 15.3
        }
      ]
    }
  ]
}
```

---

## 🔧 Troubleshooting

### Issue 1: "No module named 'ultralytics'"

**Solution:**
```bash
# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Issue 2: Low FPS / Slow Performance

**Solutions:**

1. **Use smaller model:**
   ```yaml
   detection:
     model: "yolov8n.pt"  # Fastest model
   ```

2. **Reduce input size:**
   ```yaml
   detection:
     imgsz: 416  # Smaller than default 640
   ```

3. **Skip frames:**
   ```yaml
   performance:
     skip_frames: 1  # Process every other frame
   ```

4. **Enable GPU:**
   ```bash
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
   ```

### Issue 3: "CUDA not available"

**Check CUDA:**
```python
import torch
print(torch.cuda.is_available())
print(torch.cuda.get_device_name(0))
```

**Install CUDA PyTorch:**
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### Issue 4: Inaccurate Speed/Distance

**Solution: Calibrate camera**

1. Edit `config/config.yaml`
2. Measure known distance in your scene
3. Update calibration values:
   ```yaml
   speed_estimation:
     reference_distance_meters: <your_measured_distance>
     reference_distance_pixels: <pixel_count>
   ```

### Issue 5: Webcam Not Found

**Check webcam index:**
```python
import cv2
cap = cv2.VideoCapture(0)  # Try 0, 1, 2, etc.
print(cap.isOpened())
```

---

## 🎓 Advanced Features

### 1. Custom Alert System

Edit `config/config.yaml`:
```yaml
alerts:
  enabled: true
  speed_limit_kmh: 80
  alert_classes: ["car", "truck", "bus"]
```

### 2. Zone-Based Detection

Define intrusion zones:
```yaml
alerts:
  intrusion_zones:
    - [[100, 200], [500, 200], [500, 400], [100, 400]]
```

### 3. Filter Specific Classes

Modify detection to only track vehicles:
```python
# In your code
vehicle_classes = detector.get_class_ids(['car', 'truck', 'bus'])
detections = detector.detect(frame, classes=vehicle_classes)
```

### 4. Batch Processing Multiple Videos

```bash
for video in videos/*.mp4; do
    python main.py --source "$video" --mode video --save-output --export-data --no-display
done
```

### 5. Real-Time Data Streaming

Modify `utils/logger.py` to send data to API/database in real-time.

---

## 📊 Performance Benchmarks

| Hardware | Model | Resolution | FPS | Accuracy |
|----------|-------|------------|-----|----------|
| RTX 3060 | YOLOv8n | 640x640 | 45 | Good |
| RTX 3060 | YOLOv8m | 640x640 | 25 | Very Good |
| RTX 3060 | YOLOv8x | 640x640 | 10 | Excellent |
| CPU (i7) | YOLOv8n | 640x640 | 8 | Good |
| CPU (i7) | YOLOv8m | 640x640 | 3 | Very Good |

---

## 📖 Documentation Files

- **README.md**: Project overview and features
- **QUICKSTART.md**: Quick installation and usage
- **MATH_FORMULAS.md**: Mathematical formulas explained
- **PROJECT_STRUCTURE.md**: Code architecture and modules
- **This file**: Complete setup and usage guide

---

## 🤝 Support

### Getting Help

1. **Check logs**: `output/logs/app.log`
2. **Run test script**: `python test_installation.py`
3. **Try demo**: `python demo.py`
4. **Review configuration**: `config/config.yaml`

### Common Commands Reference

```bash
# Test installation
python test_installation.py

# Run demo
python demo.py

# Webcam detection
python main.py --source 0 --mode webcam

# Video processing
python main.py --source video.mp4 --mode video --save-output --export-data

# Image processing
python main.py --source image.jpg --mode image --save-output

# IP camera
python main.py --source "rtsp://url" --mode stream

# Headless mode
python main.py --source video.mp4 --mode video --no-display --save-output
```

---

## ✅ Next Steps

1. ✅ Complete installation
2. ✅ Run `python test_installation.py`
3. ✅ Test with webcam: `python main.py --source 0 --mode webcam`
4. ✅ Process a sample video
5. ✅ Review output files in `output/`
6. ✅ Calibrate for your camera setup
7. ✅ Customize configuration for your use case
8. ✅ Deploy for production

---

## 🎉 You're Ready!

Your object detection system is now set up and ready to use. Start with the webcam test and explore the features!

```bash
python main.py --source 0 --mode webcam
```

**Happy Detecting! 🚀**
