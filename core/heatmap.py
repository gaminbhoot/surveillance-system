"""
heatmap.py — Motion heatmap rendering utilities
"""

import cv2
import numpy as np


def render_heatmap(grid_heatmap: np.ndarray, base_frame: np.ndarray) -> np.ndarray:
    """
    Overlay a colour-coded motion heatmap onto the base frame.
    Returns the composited image (480×360).
    """
    h, w = base_frame.shape[:2]
    final = base_frame.copy()

    if np.sum(grid_heatmap) == 0:
        msg = "No motion detected"
        (tw, th), _ = cv2.getTextSize(msg, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
        cv2.putText(final, msg, ((w - tw) // 2, (h + th) // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        return final

    norm = cv2.normalize(grid_heatmap, None, 0, 255,
                         cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    colored = cv2.applyColorMap(norm, cv2.COLORMAP_JET)
    colored_resized = cv2.resize(colored, (w, h))

    _, mask = cv2.threshold(norm, 1, 255, cv2.THRESH_BINARY)
    mask_resized = cv2.resize(mask, (w, h))

    alpha = 0.4
    blended = cv2.addWeighted(base_frame, alpha, colored_resized, 1 - alpha, 0)
    final[mask_resized > 0] = blended[mask_resized > 0]

    # Legend
    lx, ly = w - 200, h - 70
    cv2.rectangle(final, (lx, ly), (lx + 20, ly + 20), (0, 0, 255), -1)
    cv2.putText(final, "High Motion", (lx + 25, ly + 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.rectangle(final, (lx, ly + 30), (lx + 20, ly + 50), (255, 0, 0), -1)
    cv2.putText(final, "Low Motion", (lx + 25, ly + 45),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

    return final
