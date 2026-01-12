from __future__ import annotations

import json
import random
from typing import Dict, List, Tuple

import numpy as np
from sklearn.model_selection import train_test_split

from src import config


def save_sequence(sequence: List[np.ndarray], label: str, sample_id: int):
    label_dir = config.DATA_DIR / label
    label_dir.mkdir(parents=True, exist_ok=True)
    path = label_dir / f"{label}_{sample_id:04d}.npy"
    np.save(path, np.stack(sequence))
    return path


def load_dataset() -> Tuple[np.ndarray, np.ndarray, Dict[int, str]]:
    X, y = [], []
    label_to_idx: Dict[str, int] = {}

    for label_dir in sorted(config.DATA_DIR.glob("*")):
        if not label_dir.is_dir():
            continue
        label = label_dir.name
        if label not in label_to_idx:
            label_to_idx[label] = len(label_to_idx)
        for npy_file in label_dir.glob("*.npy"):
            seq = np.load(npy_file)
            if seq.shape[0] != config.SEQUENCE_LENGTH:
                continue  # skip incomplete clips
            
            # Normalize feature dimension to exactly NUM_LANDMARKS
            if seq.shape[1] != config.NUM_LANDMARKS:
                # Pad or truncate each frame
                normalized_frames = []
                for frame in seq:
                    if frame.shape[0] < config.NUM_LANDMARKS:
                        frame = np.concatenate([frame, np.zeros(config.NUM_LANDMARKS - frame.shape[0], dtype=np.float32)])
                    else:
                        frame = frame[:config.NUM_LANDMARKS]
                    normalized_frames.append(frame)
                seq = np.stack(normalized_frames)
            
            X.append(seq)
            y.append(label_to_idx[label])

    idx_to_label = {v: k for k, v in label_to_idx.items()}
    X = np.array(X, dtype=np.float32)
    y = np.array(y, dtype=np.int64)
    return X, y, idx_to_label


def train_val_split(
    X: np.ndarray, y: np.ndarray, test_size: float = config.TEST_SPLIT
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    return train_test_split(
        X, y, test_size=test_size, random_state=config.RANDOM_STATE, stratify=y
    )


def save_label_map(idx_to_label: Dict[int, str]):
    config.MODEL_DIR.mkdir(parents=True, exist_ok=True)
    with open(config.MODEL_DIR / "label_map.json", "w", encoding="utf-8") as f:
        json.dump(idx_to_label, f, indent=2)


def load_label_map() -> Dict[int, str]:
    with open(config.MODEL_DIR / "label_map.json", "r", encoding="utf-8") as f:
        return {int(k): v for k, v in json.load(f).items()}


def shuffle_in_unison(a: np.ndarray, b: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    assert len(a) == len(b)
    p = np.random.permutation(len(a))
    return a[p], b[p]


def get_sample_counts() -> Dict[str, int]:
    counts = {}
    for label_dir in config.DATA_DIR.glob("*"):
        if label_dir.is_dir():
            counts[label_dir.name] = len(list(label_dir.glob("*.npy")))
    return counts

