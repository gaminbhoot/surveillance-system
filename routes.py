"""
routes.py — Flask route definitions
"""

import base64
import numpy as np
import cv2
from flask import Blueprint, request, jsonify, render_template

from core import SurveillanceTracker, render_heatmap

bp = Blueprint("main", __name__)

# Module-level singletons (initialised in app.py after model download)
tracker: SurveillanceTracker = None
last_frame: np.ndarray = None


def init_tracker(model_path: str = "yolov8n.pt"):
    global tracker
    tracker = SurveillanceTracker(model_path)


# ------------------------------------------------------------------ routes

@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/upload", methods=["POST"])
def upload():
    global last_frame
    data = request.get_json()
    img_bytes = base64.b64decode(data["image"].split(",")[1])
    frame = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)

    annotated, threat_status = tracker.process_frame(frame)
    last_frame = annotated.copy()

    _, buf = cv2.imencode(".jpg", annotated)
    encoded = base64.b64encode(buf).decode()
    return jsonify({"image": "data:image/jpeg;base64," + encoded,
                    "threat": threat_status})


@bp.route("/end_feed", methods=["POST"])
def end_feed():
    global last_frame
    base = last_frame if last_frame is not None else np.zeros((360, 480, 3), dtype=np.uint8)
    final = render_heatmap(tracker.grid_heatmap, base)

    _, buf = cv2.imencode(".jpg", final)
    encoded = base64.b64encode(buf).decode()
    return jsonify({"heatmap_image": "data:image/jpeg;base64," + encoded})
