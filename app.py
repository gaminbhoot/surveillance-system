"""
app.py — Application entry point
"""

from flask import Flask
from core.model_utils import ensure_model
from routes import bp, init_tracker

def create_app(model_path: str = "yolov8n.pt") -> Flask:
    ensure_model(model_path)
    app = Flask(__name__)
    init_tracker(model_path)
    app.register_blueprint(bp)
    return app


if __name__ == "__main__":
    application = create_app()
    print(" * Open http://127.0.0.1:5000 in your browser")
    application.run(port=5000, debug=True)
