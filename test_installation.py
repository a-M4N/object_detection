"""
Test Script
Quick test to verify installation and basic functionality.
"""

import sys
import cv2
import numpy as np

def test_imports():
    """Test if all required packages are installed."""
    print("Testing imports...")
    
    try:
        import ultralytics
        print("✓ ultralytics installed")
    except ImportError:
        print("✗ ultralytics not installed")
        return False
    
    try:
        import cv2
        print(f"✓ opencv-python installed (version {cv2.__version__})")
    except ImportError:
        print("✗ opencv-python not installed")
        return False
    
    try:
        import supervision
        print("✓ supervision installed")
    except ImportError:
        print("✗ supervision not installed")
        return False
    
    try:
        import yaml
        print("✓ PyYAML installed")
    except ImportError:
        print("✗ PyYAML not installed")
        return False
    
    try:
        import pandas
        print("✓ pandas installed")
    except ImportError:
        print("✗ pandas not installed")
        return False
    
    try:
        import numpy
        print(f"✓ numpy installed (version {numpy.__version__})")
    except ImportError:
        print("✗ numpy not installed")
        return False
    
    return True


def test_yolo_model():
    """Test YOLO model loading."""
    print("\nTesting YOLO model...")
    
    try:
        from ultralytics import YOLO
        
        # Load model (will download if not present)
        print("Loading YOLOv8n model (this may take a moment on first run)...")
        model = YOLO('yolov8n.pt')
        print("✓ YOLO model loaded successfully")
        
        # Test inference on dummy image
        print("Testing inference on dummy image...")
        dummy_image = np.zeros((640, 640, 3), dtype=np.uint8)
        results = model.predict(dummy_image, verbose=False)
        print("✓ YOLO inference successful")
        
        return True
    
    except Exception as e:
        print(f"✗ YOLO test failed: {e}")
        return False


def test_webcam():
    """Test webcam access."""
    print("\nTesting webcam access...")
    
    try:
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("✗ Webcam not accessible")
            return False
        
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            print(f"✓ Webcam accessible (resolution: {frame.shape[1]}x{frame.shape[0]})")
            return True
        else:
            print("✗ Failed to read from webcam")
            return False
    
    except Exception as e:
        print(f"✗ Webcam test failed: {e}")
        return False


def test_cuda():
    """Test CUDA availability."""
    print("\nTesting CUDA availability...")
    
    try:
        import torch
        
        if torch.cuda.is_available():
            device_name = torch.cuda.get_device_name(0)
            print(f"✓ CUDA available (Device: {device_name})")
            return True
        else:
            print("⚠ CUDA not available (will use CPU)")
            return False
    
    except ImportError:
        print("⚠ PyTorch not installed (cannot check CUDA)")
        return False
    except Exception as e:
        print(f"⚠ CUDA test failed: {e}")
        return False


def test_config():
    """Test configuration file."""
    print("\nTesting configuration...")
    
    try:
        import yaml
        from pathlib import Path
        
        config_path = Path("config/config.yaml")
        
        if not config_path.exists():
            print(f"✗ Config file not found: {config_path}")
            return False
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        print("✓ Configuration file loaded successfully")
        print(f"  - Model: {config['detection']['model']}")
        print(f"  - Device: {config['detection']['device']}")
        print(f"  - Tracking: {'enabled' if config['tracking']['enabled'] else 'disabled'}")
        
        return True
    
    except Exception as e:
        print(f"✗ Config test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Object Detection System - Installation Test")
    print("=" * 60)
    
    results = []
    
    # Test imports
    results.append(("Imports", test_imports()))
    
    # Test configuration
    results.append(("Configuration", test_config()))
    
    # Test YOLO
    results.append(("YOLO Model", test_yolo_model()))
    
    # Test CUDA
    results.append(("CUDA", test_cuda()))
    
    # Test webcam
    results.append(("Webcam", test_webcam()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")
    
    # Overall result
    all_critical_passed = results[0][1] and results[1][1] and results[2][1]
    
    print("\n" + "=" * 60)
    if all_critical_passed:
        print("✓ All critical tests passed! System is ready to use.")
        print("\nNext steps:")
        print("1. Run: python main.py --source 0 --mode webcam")
        print("2. Or: python main.py --source video.mp4 --mode video")
    else:
        print("✗ Some critical tests failed. Please fix the issues above.")
        print("\nTroubleshooting:")
        print("1. Ensure virtual environment is activated")
        print("2. Run: pip install -r requirements.txt")
        print("3. Check config/config.yaml exists")
    print("=" * 60)
    
    return 0 if all_critical_passed else 1


if __name__ == '__main__':
    sys.exit(main())
