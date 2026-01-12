"""
Run real-time inference from webcam using trained model.

Usage:
    python -m src.inference --model-path models/isl_lstm.h5
"""
from __future__ import annotations

import argparse
import collections
from typing import Deque

import cv2
import numpy as np
import tensorflow as tf

from src import config
from src.utils.data_utils import load_label_map
from src.utils.mediapipe_utils import (
    create_hand_tracker,
    create_face_tracker,
    create_pose_tracker,
    extract_combined_landmarks,
    draw_info,
)


def smooth_prediction(probs: np.ndarray, history: Deque[int], threshold: float):
    pred_idx = int(np.argmax(probs))
    confidence = float(np.max(probs))
    
    if confidence >= threshold:
        history.append(pred_idx)
    
    # If history is full, use most common prediction from history
    # BUT only if current confidence isn't significantly higher than smoothed
    if len(history) == history.maxlen:
        counts = collections.Counter(history)
        smoothed_idx = counts.most_common(1)[0][0]
        smoothed_conf = float(probs[smoothed_idx])
        
        # If current prediction has much higher confidence, trust it over history
        if confidence > smoothed_conf + 0.15:  # 15% threshold
            return pred_idx, confidence
        
        return smoothed_idx, smoothed_conf
    
    return pred_idx, confidence


def run(model_path: str, threshold: float):
    label_map = load_label_map()
    model = tf.keras.models.load_model(model_path)
    cap = cv2.VideoCapture(0)
    # Track hands, face, AND upper body pose (chest, head, shoulders) for complete ISL signs
    hands = create_hand_tracker(static_image_mode=False, max_num_hands=2)
    face_mesh = create_face_tracker(static_image_mode=False)
    pose = create_pose_tracker(static_image_mode=False)
    buffer: Deque[np.ndarray] = collections.deque(maxlen=config.SEQUENCE_LENGTH)
    history: Deque[int] = collections.deque(maxlen=5)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Extract combined hand + face + pose (chest, head, upper body) landmarks
            landmarks = extract_combined_landmarks(frame, hands, face_mesh, pose, draw=True)
            if landmarks is not None:
                buffer.append(landmarks)
            if len(buffer) == config.SEQUENCE_LENGTH:
                input_seq = np.expand_dims(np.array(buffer), axis=0)
                probs = model.predict(input_seq, verbose=0)[0]
                pred_idx, conf = smooth_prediction(probs, history, threshold)
                pred_label = label_map.get(pred_idx, "unknown")
                
                # Show top 3 predictions for debugging
                top3 = np.argsort(probs)[-3:][::-1]
                top3_labels = [label_map.get(i, "?") for i in top3]
                top3_probs = [probs[i] for i in top3]
                
                # Only show prediction if confidence is above threshold
                if conf >= threshold:
                    draw_info(frame, f"{pred_label} ({conf:.2f})", color=(0, 255, 0))
                else:
                    draw_info(frame, f"Low confidence: {pred_label} ({conf:.2f})", color=(0, 165, 255))
                
                # Debug info (smaller text)
                debug_text = f"Top3: {top3_labels[0]}({top3_probs[0]:.2f}) {top3_labels[1]}({top3_probs[1]:.2f}) {top3_labels[2]}({top3_probs[2]:.2f})"
                cv2.putText(frame, debug_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            else:
                draw_info(frame, f"Collecting frames... ({len(buffer)}/{config.SEQUENCE_LENGTH})")

            cv2.imshow("ISL Inference", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        hands.close()
        face_mesh.close()
        pose.close()
        cv2.destroyAllWindows()


def parse_args():
    parser = argparse.ArgumentParser(description="Run real-time ISL inference.")
    parser.add_argument("--model-path", type=str, default=str(config.MODEL_DIR / "isl_lstm.h5"))
    parser.add_argument(
        "--threshold", type=float, default=config.MIN_CONFIDENCE, help="Confidence threshold"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run(args.model_path, args.threshold)


