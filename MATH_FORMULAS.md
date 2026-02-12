# Mathematical Formulas and Algorithms

This document explains the mathematical foundations of the estimation algorithms used in the object detection system.

## Table of Contents
1. [Speed Estimation](#speed-estimation)
2. [Height Estimation](#height-estimation)
3. [Distance Estimation](#distance-estimation)
4. [Direction Detection](#direction-detection)
5. [Camera Calibration](#camera-calibration)

---

## Speed Estimation

### Overview
Vehicle speed is estimated by tracking the object's displacement between consecutive frames and converting pixel movement to real-world distance.

### Formula

```
Speed (km/h) = (Pixel Displacement × Scale Factor × FPS × 3.6) / 1000
```

Where:
- **Pixel Displacement**: Distance moved in pixels between frames
- **Scale Factor**: Conversion ratio from pixels to meters
- **FPS**: Frames per second of the video
- **3.6**: Conversion factor from m/s to km/h (1 m/s = 3.6 km/h)

### Detailed Steps

#### 1. Calculate Pixel Displacement
```
Given two consecutive positions:
  P1 = (x1, y1) at frame t
  P2 = (x2, y2) at frame t+1

Displacement (pixels) = √[(x2 - x1)² + (y2 - y1)²]
```

#### 2. Calculate Scale Factor
```
Scale Factor = Real World Distance (m) / Pixel Distance (px)

Example:
  If 10 meters in real world = 200 pixels in image
  Scale Factor = 10 / 200 = 0.05 m/px
```

#### 3. Convert to Real-World Displacement
```
Real Displacement (m) = Pixel Displacement × Scale Factor
```

#### 4. Calculate Speed
```
Time Elapsed (s) = Frame Difference / FPS

Speed (m/s) = Real Displacement / Time Elapsed

Speed (km/h) = Speed (m/s) × 3.6
```

### Smoothing
To reduce noise, speeds are averaged over a sliding window:

```
Smoothed Speed = (1/N) × Σ(Speed_i) for i = 1 to N

Where N = smoothing window size (typically 5-10 frames)
```

### Limitations
- Assumes constant camera position
- Accuracy depends on calibration quality
- Perspective distortion affects accuracy at different distances
- Works best for objects moving parallel to camera plane

### Improving Accuracy
1. **Perspective Transformation**: Apply homography to get bird's-eye view
2. **Camera Calibration**: Use precise focal length and distortion parameters
3. **Multiple Reference Points**: Use different scale factors for different distances
4. **Temporal Filtering**: Apply Kalman filter for smoother estimates

---

## Height Estimation

### Overview
Person height is estimated using the bounding box dimensions and camera parameters.

### Basic Formula (Ratio-Based)

```
Height (cm) = (Bbox Height / Reference Bbox Height) × Reference Height
```

Where:
- **Bbox Height**: Current bounding box height in pixels
- **Reference Bbox Height**: Calibrated reference height in pixels
- **Reference Height**: Known average person height (e.g., 170 cm)

### Advanced Formula (Distance-Based)

```
Height (m) = (Bbox Height × Distance × Sensor Height) / (Focal Length × Image Height)
```

Where:
- **Bbox Height**: Bounding box height in pixels
- **Distance**: Distance from camera in meters
- **Sensor Height**: Physical camera sensor height in mm
- **Focal Length**: Camera focal length in pixels
- **Image Height**: Image height in pixels

### Simplified Pinhole Model

```
Height (m) = (Bbox Height × Distance) / Focal Length
```

This assumes the object is perpendicular to the camera's optical axis.

### Calibration Process

1. **Automatic Calibration**:
   ```
   Collect N person detections (N ≈ 10)
   Reference Bbox Height = median(Bbox Heights)
   ```

2. **Manual Calibration**:
   ```
   Given: Known person height = H_actual (cm)
          Measured bbox height = H_bbox (pixels)
   
   Reference Bbox Height = H_bbox × (Reference Height / H_actual)
   ```

### Distance Correction

When distance information is available:
```
Corrected Height = Base Height × (Distance / Reference Distance)

Where Reference Distance ≈ 5 meters (typical calibration distance)
```

### Limitations
- Assumes person is standing upright
- Accuracy decreases with distance
- Affected by camera angle and perspective
- Bounding box may not capture full height

---

## Distance Estimation

### Overview
Distance is estimated using the pinhole camera model and known object dimensions.

### Pinhole Camera Model

```
Distance (m) = (Known Object Height × Focal Length) / Bbox Height
```

Where:
- **Known Object Height**: Real-world height of object in meters
- **Focal Length**: Camera focal length in pixels
- **Bbox Height**: Bounding box height in pixels

### Derivation

From similar triangles in pinhole camera model:
```
Object Height / Distance = Bbox Height / Focal Length

Rearranging:
Distance = (Object Height × Focal Length) / Bbox Height
```

### Known Object Heights (Default Values)

| Object Class | Height (m) |
|-------------|-----------|
| Person      | 1.7       |
| Car         | 1.5       |
| Truck       | 3.0       |
| Bus         | 3.5       |
| Bicycle     | 1.0       |
| Motorcycle  | 1.2       |

### Focal Length Calculation

If focal length is unknown, calibrate using a known distance:

```
Focal Length (pixels) = (Known Distance × Bbox Height) / Object Height

Example:
  Person at 5 meters with bbox height 200 pixels
  Focal Length = (5 × 200) / 1.7 ≈ 588 pixels
```

### Alternative: Focal Length from Camera Specs

```
Focal Length (pixels) = (Focal Length (mm) × Image Width (pixels)) / Sensor Width (mm)

Example:
  Focal Length = 3.6 mm
  Image Width = 1920 pixels
  Sensor Width = 6.17 mm
  
  Focal Length (pixels) = (3.6 × 1920) / 6.17 ≈ 1121 pixels
```

### Limitations
- Requires accurate object height database
- Assumes object is perpendicular to camera
- Affected by camera distortion
- Less accurate for objects far from camera center

---

## Direction Detection

### Overview
Movement direction is determined by analyzing the trajectory of tracked objects.

### Movement Vector

```
Given positions over time:
  P_start = (x_start, y_start) at frame t
  P_end = (x_end, y_end) at frame t+n

Movement Vector = (dx, dy)
  where dx = x_end - x_start
        dy = y_end - y_start
```

### Displacement Magnitude

```
Displacement = √(dx² + dy²)
```

### Movement Angle

```
Angle (radians) = arctan2(dy, dx)
Angle (degrees) = arctan2(dy, dx) × 180 / π
```

### Direction Classification (8-way)

Based on angle ranges:

| Angle Range (°) | Direction |
|----------------|-----------|
| -22.5 to 22.5  | Right     |
| 22.5 to 67.5   | Down-Right|
| 67.5 to 112.5  | Down      |
| 112.5 to 157.5 | Down-Left |
| 157.5 to 202.5 | Left      |
| 202.5 to 247.5 | Up-Left   |
| 247.5 to 292.5 | Up        |
| 292.5 to 337.5 | Up-Right  |

### Velocity Calculation

```
Velocity (pixels/second) = (dx, dy) × FPS / Frame Count

Where Frame Count = number of frames in trajectory history
```

### Approaching Detection

Determine if object is approaching camera:

```
Distance History: [d1, d2, d3, ..., dn]

If d_n < d_1:
  Object is approaching (distance decreasing)
Else:
  Object is receding (distance increasing)
```

---

## Camera Calibration

### Intrinsic Parameters

Camera matrix:
```
K = | fx  0   cx |
    | 0   fy  cy |
    | 0   0   1  |
```

Where:
- **fx, fy**: Focal lengths in x and y (pixels)
- **cx, cy**: Principal point (image center)

### Distortion Coefficients

Radial and tangential distortion:
```
Distortion = [k1, k2, p1, p2, k3]
```

Where:
- **k1, k2, k3**: Radial distortion coefficients
- **p1, p2**: Tangential distortion coefficients

### Perspective Transformation

For bird's-eye view (useful for accurate speed estimation):

1. **Define Source Points** (trapezoid in image):
   ```
   src_points = [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
   ```

2. **Define Destination Points** (rectangle in real-world):
   ```
   dst_points = [(0, 0), (width, 0), (width, height), (0, height)]
   ```

3. **Calculate Homography Matrix**:
   ```
   H = findHomography(src_points, dst_points)
   ```

4. **Transform Points**:
   ```
   real_world_point = H × image_point
   ```

### Calibration Using Checkerboard

For precise calibration:

1. Capture multiple images of checkerboard pattern
2. Detect corners in each image
3. Solve for camera matrix and distortion coefficients
4. Use OpenCV's `calibrateCamera()` function

---

## Error Analysis

### Speed Estimation Error

```
Error_speed = √[(∂S/∂d × σ_d)² + (∂S/∂f × σ_f)² + (∂S/∂s × σ_s)²]
```

Where:
- **σ_d**: Error in displacement measurement
- **σ_f**: Error in FPS
- **σ_s**: Error in scale factor

### Distance Estimation Error

```
Error_distance = Distance × √[(σ_h/h)² + (σ_f/f)² + (σ_b/b)²]
```

Where:
- **σ_h**: Error in known height
- **σ_f**: Error in focal length
- **σ_b**: Error in bbox height measurement

---

## Best Practices

1. **Calibration**:
   - Calibrate with objects at multiple distances
   - Use precise measurements for reference distances
   - Recalibrate when camera position changes

2. **Accuracy**:
   - Use higher resolution for better bbox accuracy
   - Apply lens distortion correction
   - Use perspective transformation for ground plane measurements

3. **Robustness**:
   - Apply temporal smoothing (moving average, Kalman filter)
   - Validate estimates against reasonable ranges
   - Handle occlusions and partial detections

4. **Performance**:
   - Cache computed values when possible
   - Use vectorized operations (NumPy)
   - Optimize for real-time processing

---

## References

1. Hartley, R., & Zisserman, A. (2003). Multiple View Geometry in Computer Vision
2. Zhang, Z. (2000). A flexible new technique for camera calibration
3. Forsyth, D. A., & Ponce, J. (2002). Computer Vision: A Modern Approach
4. OpenCV Documentation: Camera Calibration and 3D Reconstruction
