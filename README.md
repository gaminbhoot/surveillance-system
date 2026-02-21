# 🔍 Live Webcam Surveillance System

> Real-time person detection, multi-object tracking, loitering alerts, and motion heatmaps — all running in your browser via a local Flask server.

---

## 🚀 Live Demo

**[▶ Try the Interactive Prototype →](https://surveillance-demo.netlify.app)**
*(Click to see the UI, deployment walkthrough, and feature showcase — no installation needed)*

> The prototype above demonstrates the full UI and simulated detections. For real inference on your own webcam, follow the local setup below.

---

## ✨ Features

| Feature | Description |
|---|---|
| 👤 Person Detection | YOLOv8n detects people in real time |
| 🎯 Multi-Object Tracking | DeepSORT assigns persistent IDs across frames |
| 🚨 Loitering Alerts | Red bounding box + banner when a person is stationary too long |
| 🗺️ Motion Heatmap | JET-coloured overlay rendered on "End Feed" |
| 🌐 Browser-based | No desktop app needed — just open `localhost:5000` |

---

## 🗂️ Repository Structure

```
surveillance-system/
│
├── app.py                  # Flask application factory & entry point
├── routes.py               # /upload and /end_feed API endpoints
├── requirements.txt
│
├── core/
│   ├── __init__.py
│   ├── tracker.py          # YOLOv8 + DeepSORT person tracking
│   ├── heatmap.py          # Motion heatmap rendering
│   └── model_utils.py      # Auto-download YOLOv8 weights
│
├── templates/
│   └── index.html          # Jinja2 page template
│
└── static/
    ├── style.css           # Animated gradient UI styles
    └── main.js             # Webcam capture & fetch loop
```

---

## 🛠️ Local Setup

### Prerequisites
- Python 3.10+
- A webcam
- ~50 MB disk space for the YOLOv8n model (auto-downloaded on first run)

### Install

```bash
git clone https://github.com/YOUR_USERNAME/surveillance-system.git
cd surveillance-system

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### Run

```bash
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

> On first launch the YOLOv8n weights (~6 MB) are downloaded automatically.

---

## ⚙️ How It Works

```
Browser (JS)
  │  captures frame every 250 ms via <canvas>
  │  POST /upload  { image: base64 JPEG }
  ▼
Flask /upload
  │  decode → YOLOv8n detect → DeepSORT track
  │  update grid_heatmap, check loitering
  │  annotate frame → return base64 + threat JSON
  ▼
Browser
  │  display annotated frame
  │  show/hide loitering banner
  ▼
  [End Feed clicked]
  │  POST /end_feed
  │  overlay heatmap onto last frame
  └─ display final heatmap
```

### Loitering Detection Logic

A person is flagged as *loitering* when their bounding-box centre moves less than **10 px** for more than **150 consecutive frames** (~37 seconds at 4 fps).  
Both thresholds are tunable constants in `core/tracker.py`:

```python
LOITERING_THRESHOLD = 150   # frames
MOVEMENT_TOLERANCE  = 10    # pixels
```

---

## 🖼️ Screenshots

| Live Feed with Tracking | Motion Heatmap |
|---|---|
| ![tracking](docs/tracking.png) | ![heatmap](docs/heatmap.png) |

---

## 🔭 Roadmap

- [ ] WebSocket streaming (remove polling delay)
- [ ] Multi-camera support
- [ ] Alert email / webhook notifications
- [ ] Save annotated video to disk
- [ ] Docker deployment

---

## 📄 License

MIT — see [LICENSE](LICENSE).
