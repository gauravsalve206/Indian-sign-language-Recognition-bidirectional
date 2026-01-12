"""
Collect custom ISL gesture dataset using webcam + MediaPipe.

Usage:
    python -m src.data_collection --labels hello thank_you yes no --samples 20
Press 'c' to capture a clip, 'q' to quit.
"""
from __future__ import annotations

import argparse
import time
from typing import List

import cv2
import numpy as np

from src import config
from src.utils.data_utils import save_sequence, get_sample_counts
from src.utils.mediapipe_utils import (
    create_hand_tracker,
    create_face_tracker,
    create_pose_tracker,
    extract_combined_landmarks,
    draw_info,
)


def collect_gesture(labels: List[str], samples_per_label: int):
    counts = get_sample_counts()
    # Track hands, face, AND upper body pose (chest, head, shoulders) for complete ISL signs
    hands = create_hand_tracker(static_image_mode=False, max_num_hands=2)
    face_mesh = create_face_tracker(static_image_mode=False)
    pose = create_pose_tracker(static_image_mode=False)

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    try:
        for label in labels:
            existing = counts.get(label, 0)
            for idx in range(existing, existing + samples_per_label):
                sequence = []
                print(f"[{label}] Sample {idx + 1}/{existing + samples_per_label}")
                ready_time = time.time() + 2
                while time.time() < ready_time:
                    ret, frame = cap.read()
                    if not ret:
                        continue
                    draw_info(frame, f"Get ready: {label}")
                    cv2.imshow("Collect", frame)
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        return

                while len(sequence) < config.SEQUENCE_LENGTH:
                    ret, frame = cap.read()
                    if not ret:
                        continue

                    # Extract combined hand + face + pose (chest, head, upper body) landmarks
                    landmarks = extract_combined_landmarks(frame, hands, face_mesh, pose, draw=True)
                    if landmarks is not None:
                        sequence.append(landmarks)
                        draw_info(
                            frame,
                            f"{label}: {len(sequence)}/{config.SEQUENCE_LENGTH}",
                        )
                    else:
                        draw_info(frame, "No hands/face/pose detected", color=(0, 0, 255))

                    cv2.imshow("Collect", frame)
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        return

                path = save_sequence(sequence, label, idx)
                print(f"Saved {path}")
    finally:
        cap.release()
        hands.close()
        face_mesh.close()
        pose.close()
        cv2.destroyAllWindows()


def parse_args():
    parser = argparse.ArgumentParser(description="Collect ISL gesture dataset.")
    parser.add_argument(
        "--labels",
        nargs="+",
        required=True,
        help="Gesture labels to record (e.g., hello thank_you yes no)",
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=20,
        help="Samples to record per label.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    collect_gesture(args.labels, args.samples)


