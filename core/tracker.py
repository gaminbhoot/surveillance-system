"""
tracker.py — Person detection and DeepSORT tracking logic
"""

import cv2
import numpy as np
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
from math import sqrt


LOITERING_THRESHOLD = 150   # frames before loitering alert
MOVEMENT_TOLERANCE = 10     # pixel distance considered "still"


class SurveillanceTracker:
    def __init__(self, model_path: str = "yolov8n.pt"):
        self.model = YOLO(model_path)
        self.tracker = DeepSort(max_age=30)
        self.track_data: dict = {}
        self.grid_heatmap = np.zeros((36, 48), dtype=np.float32)

    def process_frame(self, frame: np.ndarray) -> tuple[np.ndarray, dict]:
        """
        Run detection + tracking on a single frame.
        Returns the annotated frame and a threat-status dict.
        """
        results = self.model(frame, verbose=False)[0]
        detections = self._parse_detections(results)
        tracks = self.tracker.update_tracks(detections, frame=frame)

        current_loitering_ids = []
        for track in tracks:
            if not track.is_confirmed():
                continue
            track_id = track.track_id
            l, t, r, b = track.to_ltrb()
            cx, cy = int((l + r) / 2), int((t + b) / 2)

            # Update heatmap
            cell_y = min(cy // 10, 35)
            cell_x = min(cx // 10, 47)
            self.grid_heatmap[cell_y, cell_x] += 1

            # Update loitering state
            self._update_loitering(track_id, cx, cy)

            # Draw bounding box
            is_loitering = self.track_data.get(track_id, {}).get("is_loitering", False)
            color = (0, 0, 255) if is_loitering else (0, 255, 0)
            cv2.rectangle(frame, (int(l), int(t)), (int(r), int(b)), color, 2)
            cv2.putText(frame, f"Person ID: {track_id}", (int(l), int(t) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            if is_loitering:
                cv2.putText(frame, "LOITERING ALERT", (int(l), int(t) - 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                current_loitering_ids.append(track_id)

        threat_status = {
            "loitering_detected": bool(current_loitering_ids),
            "active_threat_ids": current_loitering_ids,
        }
        return frame, threat_status

    # ------------------------------------------------------------------ helpers
    def _parse_detections(self, results):
        detections = []
        for box, score, cls in zip(
            results.boxes.xyxy.cpu().numpy(),
            results.boxes.conf.cpu().numpy(),
            results.boxes.cls.cpu().numpy(),
        ):
            if self.model.model.names[int(cls)] == "person":
                x, y, x2, y2 = box
                detections.append(([x, y, x2 - x, y2 - y], score, "person"))
        return detections

    def _update_loitering(self, track_id, cx, cy):
        if track_id not in self.track_data:
            self.track_data[track_id] = {
                "last_pos": (cx, cy),
                "still_counter": 0,
                "is_loitering": False,
            }
        else:
            td = self.track_data[track_id]
            dist = sqrt((cx - td["last_pos"][0]) ** 2 + (cy - td["last_pos"][1]) ** 2)
            if dist < MOVEMENT_TOLERANCE:
                td["still_counter"] += 1
            else:
                td["still_counter"] = 0
                td["last_pos"] = (cx, cy)
            if td["still_counter"] > LOITERING_THRESHOLD:
                td["is_loitering"] = True
