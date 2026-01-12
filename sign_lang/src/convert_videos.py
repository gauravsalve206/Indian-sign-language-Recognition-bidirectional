"""
Convert ISL video dataset into landmark sequences using hands + face.

Expected video folder structure:

    video_dataset/
      hello/
        hello.mp4
      thank_you/
        thank_you.mp4
      ...

This script will:
- Extract frames from each video
- Extract combined hand + face + pose (chest, head, upper body) landmarks from each frame
- Use sliding window to create multiple sequences of SEQUENCE_LENGTH frames
- Save to: dataset/<label>/<label>_####.npy

Even with ONE video per sign, this creates multiple training samples by sliding
a window across the video frames.

Usage (from project root):
    python -m src.convert_videos --root video_dataset --stride 10
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np

from src import config
from src.utils.data_utils import get_sample_counts, save_sequence
from src.utils.mediapipe_utils import (
    create_hand_tracker,
    create_face_tracker,
    create_pose_tracker,
    extract_combined_landmarks,
)


def extract_landmarks_from_video(
    video_path: Path, hands, face_mesh, pose, stride: int = 10
) -> list[np.ndarray]:
    
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"[WARN] Cannot open video: {video_path}")
        return []

    all_landmarks = []
    frame_count = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Extract  landmarks 
            landmarks = extract_combined_landmarks(frame, hands, face_mesh, pose, draw=False)
            if landmarks is not None:
                all_landmarks.append(landmarks)
            frame_count += 1

    finally:
        cap.release()

    print(f"  Extracted {len(all_landmarks)} valid frames from {frame_count} total frames")
    return all_landmarks


def create_sequences_from_landmarks(
    landmarks_list: list[np.ndarray], stride: int
) -> list[np.ndarray]:
   
    
    normalized_list = []
    for lm in landmarks_list:
        if lm is None:
            normalized_list.append(np.zeros(config.NUM_LANDMARKS, dtype=np.float32))
        elif lm.shape[0] != config.NUM_LANDMARKS:
            # Pad or truncate to correct size
            if lm.shape[0] < config.NUM_LANDMARKS:
                # Pad with zeros
                pad_size = config.NUM_LANDMARKS - lm.shape[0]
                lm = np.concatenate([lm, np.zeros(pad_size, dtype=np.float32)])
            else:
                # Truncate
                lm = lm[:config.NUM_LANDMARKS]
            normalized_list.append(lm)
        else:
            normalized_list.append(lm)

    if len(normalized_list) < config.SEQUENCE_LENGTH:
        # Video too short: pad with zeros
        print(f"  [WARN] Video has only {len(normalized_list)} frames, padding to {config.SEQUENCE_LENGTH}")
        while len(normalized_list) < config.SEQUENCE_LENGTH:
            normalized_list.append(np.zeros(config.NUM_LANDMARKS, dtype=np.float32))

    sequences = []
    # Slide window across the video
    for start_idx in range(0, len(normalized_list) - config.SEQUENCE_LENGTH + 1, stride):
        seq = normalized_list[start_idx : start_idx + config.SEQUENCE_LENGTH]
        # Ensure all arrays in seq have the same shape before stacking
        seq_arrays = []
        for arr in seq:
            if arr.shape[0] != config.NUM_LANDMARKS:
                if arr.shape[0] < config.NUM_LANDMARKS:
                    arr = np.concatenate([arr, np.zeros(config.NUM_LANDMARKS - arr.shape[0], dtype=np.float32)])
                else:
                    arr = arr[:config.NUM_LANDMARKS]
            seq_arrays.append(arr)
        sequences.append(np.stack(seq_arrays))

    return sequences


def convert_video_dataset(root: Path, stride: int = 10):
   
    if not root.exists():
        raise SystemExit(f"Video dataset root not found: {root}")

    counts = get_sample_counts()
    hands = create_hand_tracker(static_image_mode=False, max_num_hands=2)
    face_mesh = create_face_tracker(static_image_mode=False)
    pose = create_pose_tracker(static_image_mode=False)

    try:
        for label_dir in sorted(root.glob("*")):
            if not label_dir.is_dir():
                continue

            label = label_dir.name
            existing = counts.get(label, 0)
            idx = existing

            # Find video files
            video_files = sorted(
                [
                    p
                    for p in label_dir.glob("*")
                    if p.suffix.lower() in {".mp4", ".avi", ".mov", ".mkv", ".webm"}
                ]
            )
            if not video_files:
                print(f"[WARN] No videos found in {label_dir}")
                continue

            print(f"\n[{label}] Processing {len(video_files)} video(s)")

            for video_path in video_files:
                print(f"  Processing: {video_path.name}")

                # Extract landmarks from all frames
                landmarks_list = extract_landmarks_from_video(video_path, hands, face_mesh, pose, stride)
                if not landmarks_list:
                    print(f"  [WARN] No landmarks extracted from {video_path.name}, skipping")
                    continue

                # Create sequences using sliding window
                sequences = create_sequences_from_landmarks(landmarks_list, stride)
                print(f"  Created {len(sequences)} sequences from this video")

                # Save each sequence
                for seq in sequences:
                    # Convert sequence (30, 1530) to list of arrays for save_sequence
                    seq_list = [seq[i] for i in range(config.SEQUENCE_LENGTH)]
                    save_sequence(seq_list, label, idx)
                    idx += 1

                print(f"  Saved sequences {label}_{existing:04d} to {label}_{idx-1:04d}")

    finally:
        hands.close()
        face_mesh.close()
        pose.close()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Convert ISL video dataset to landmark sequences (hands + face)."
    )
    parser.add_argument(
        "--root",
        type=str,
        default="video_dataset",
        help="Path to video dataset root folder (contains one subfolder per label).",
    )
    parser.add_argument(
        "--stride",
        type=int,
        default=10,
        help="Step size for sliding window (lower = more overlap, more sequences). Default: 10",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    convert_video_dataset(Path(args.root), stride=args.stride)

