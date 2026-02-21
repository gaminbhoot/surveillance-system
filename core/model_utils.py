"""
model_utils.py — Model download helpers
"""

import os
import urllib.request


YOLO_URL = "https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt"


def ensure_model(model_path: str = "yolov8n.pt") -> None:
    """Download YOLOv8n weights if they don't exist locally."""
    if os.path.exists(model_path):
        return
    print(f"[model_utils] '{model_path}' not found — downloading from GitHub …")
    try:
        import gdown
        gdown.download(YOLO_URL, model_path, quiet=False)
    except ImportError:
        urllib.request.urlretrieve(YOLO_URL, model_path)
    print("[model_utils] Download complete.")
