# Object Detection System - Quick Start Guide

## Installation Steps

### 1. Create Virtual Environment
```bash
cd c:\Users\ASUS\OneDrive\Documents\object_detection
python -m venv venv
```

### 2. Activate Virtual Environment
```bash
# Windows
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Verify Installation
```bash
python -c "import ultralytics; import cv2; import supervision; print('All dependencies installed successfully!')"
```

## Quick Test

### Test with Webcam
```bash
python main.py --source 0 --mode webcam
```

### Test with Video File
```bash
python main.py --source path/to/video.mp4 --mode video --save-output --export-data
```

### Test with Image
```bash
python main.py --source path/to/image.jpg --mode image --save-output
```

## Example Commands

### 1. Basic Detection (Webcam)
```bash
python main.py --source 0 --mode webcam
```

### 2. Video Processing with All Features
```bash
python main.py --source video.mp4 --mode video --save-output --export-data
```

### 3. IP Camera Stream
```bash
python main.py --source "rtsp://username:password@192.168.1.100:554/stream" --mode stream
```

### 4. Headless Processing (No Display)
```bash
python main.py --source video.mp4 --mode video --save-output --export-data --no-display
```

### 5. Custom Configuration
```bash
python main.py --source video.mp4 --mode video --config config/custom_config.yaml
```

## Configuration Tips

### For Better Speed (Real-time Performance)
Edit `config/config.yaml`:
```yaml
detection:
  model: "yolov8n.pt"  # Use nano model
  imgsz: 416  # Reduce input size
  
performance:
  skip_frames: 1  # Process every other frame
```

### For Better Accuracy
```yaml
detection:
  model: "yolov8x.pt"  # Use extra-large model
  confidence_threshold: 0.3  # Lower threshold
  imgsz: 640
```

### For Specific Object Classes
```yaml
# In your Python code, filter classes:
# vehicle_classes = detector.get_class_ids(['car', 'truck', 'bus'])
# detections = detector.detect(frame, classes=vehicle_classes)
```

## Output Files

After processing, check these directories:

### Videos
```
output/videos/output_<timestamp>.mp4
```

### Data Exports
```
output/data/detections_<timestamp>.csv
output/data/detections_<timestamp>.json
```

### Logs
```
output/logs/app.log
```

## Troubleshooting

### Issue: "No module named 'ultralytics'"
**Solution:** Activate virtual environment and install dependencies
```bash
venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: Low FPS
**Solutions:**
1. Use smaller YOLO model (yolov8n)
2. Reduce input image size
3. Enable GPU (install CUDA)
4. Process fewer frames (skip_frames)

### Issue: "CUDA not available"
**Solution:** Install PyTorch with CUDA support
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### Issue: Inaccurate Speed/Distance
**Solution:** Calibrate camera parameters in `config/camera_calibration.yaml`

## Camera Calibration

For accurate measurements:

1. Measure a known distance in your scene (e.g., 10 meters)
2. Count the pixel distance in the video
3. Update `config/config.yaml`:
```yaml
speed_estimation:
  reference_distance_meters: 10.0
  reference_distance_pixels: 200  # Your measured pixels
```

## Keyboard Controls

When display window is active:
- **Q**: Quit application
- **ESC**: Quit application (in some systems)

## Performance Benchmarks

| Model | GPU | FPS | Accuracy |
|-------|-----|-----|----------|
| YOLOv8n | RTX 3060 | ~45 | Good |
| YOLOv8s | RTX 3060 | ~35 | Better |
| YOLOv8m | RTX 3060 | ~25 | Very Good |
| YOLOv8l | RTX 3060 | ~15 | Excellent |
| YOLOv8x | RTX 3060 | ~10 | Best |

## Next Steps

1. ✅ Install dependencies
2. ✅ Test with webcam
3. ✅ Process a sample video
4. ✅ Review output files
5. ✅ Calibrate for your camera
6. ✅ Customize configuration
7. ✅ Deploy for your use case

## Support

For issues or questions:
1. Check logs in `output/logs/app.log`
2. Review configuration in `config/config.yaml`
3. Verify camera calibration
4. Test with different YOLO models

## Advanced Usage

### Custom Alert System
Edit `config/config.yaml`:
```yaml
alerts:
  enabled: true
  speed_limit_kmh: 60
  alert_classes: ["car", "truck"]
```

### Zone-based Detection
Define intrusion zones:
```yaml
alerts:
  intrusion_zones:
    - [[100, 200], [500, 200], [500, 400], [100, 400]]
```

### Export Specific Data
Choose export format:
```yaml
output:
  data_format: "csv"  # or "json" or "both"
```
