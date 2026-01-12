"""
Real-time CNN-based ISL recognition from webcam (no MediaPipe).

Usage:
    python -m src.inference_cnn --model-path models/isl_cnn.h5
"""
from __future__ import annotations

import argparse

import cv2
import numpy as np
import tensorflow as tf

from src import config
from src.utils.data_utils import load_label_map
from src.utils.mediapipe_utils import draw_info


def preprocess_frame(frame):
    """Convert BGR frame to CNN input: grayscale, resize, binarize, normalize."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, (config.IMAGE_SIZE, config.IMAGE_SIZE))
    _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    bw = bw.astype("float32") / 255.0
    bw = np.expand_dims(bw, axis=-1)  # (H, W, 1)
    bw = np.expand_dims(bw, axis=0)   # (1, H, W, 1)
    return bw


def run(model_path: str):
    label_map = load_label_map()
    model = tf.keras.models.load_model(model_path)

    cap = cv2.VideoCapture(0)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            inp = preprocess_frame(frame)
            probs = model.predict(inp, verbose=0)[0]
            idx = int(np.argmax(probs))
            conf = float(np.max(probs))
            label = label_map.get(idx, "unknown")

            draw_info(frame, f"{label} ({conf:.2f})")
            cv2.imshow("ISL CNN Inference", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


def parse_args():
    parser = argparse.ArgumentParser(description="Run real-time CNN ISL inference.")
    parser.add_argument(
        "--model-path",
        type=str,
        default=str(config.MODEL_DIR / "isl_cnn.h5"),
        help="Path to CNN model file.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run(args.model_path)


