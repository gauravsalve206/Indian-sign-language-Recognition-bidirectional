from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

import cv2
import numpy as np
from sklearn.model_selection import train_test_split

from src import config


def preprocess_image(path: Path) -> np.ndarray:
    """Load an image, convert to grayscale, resize, binarize, normalize."""
    img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Could not read image: {path}")
    img = cv2.resize(img, (config.IMAGE_SIZE, config.IMAGE_SIZE))
    # Optional: binarize to mimic black/white dataset
    _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    img = img.astype("float32") / 255.0
    # Add channel dimension
    img = np.expand_dims(img, axis=-1)  # (H, W, 1)
    return img


def load_image_dataset(
    root: Path,
) -> Tuple[np.ndarray, np.ndarray, Dict[int, str]]:
    """
    Load images from root/label/*.jpg|png into X, y.
    """
    X, y = [], []
    label_to_idx: Dict[str, int] = {}

    for label_dir in sorted(root.glob("*")):
        if not label_dir.is_dir():
            continue
        label = label_dir.name
        if label not in label_to_idx:
            label_to_idx[label] = len(label_to_idx)
        idx = label_to_idx[label]

        for img_path in label_dir.glob("*"):
            if img_path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
                continue
            try:
                img = preprocess_image(img_path)
            except Exception as exc:  # pragma: no cover - debug / robustness
                print(f"[WARN] Skipping {img_path}: {exc}")
                continue
            X.append(img)
            y.append(idx)

    if not X:
        raise SystemExit(f"No images found under {root}")

    X = np.stack(X).astype("float32")
    y = np.array(y, dtype=np.int64)
    idx_to_label = {v: k for k, v in label_to_idx.items()}
    return X, y, idx_to_label


def train_val_split_images(
    X: np.ndarray, y: np.ndarray, test_size: float = config.TEST_SPLIT
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    return train_test_split(
        X, y, test_size=test_size, random_state=config.RANDOM_STATE, stratify=y
    )


