"""
Train a CNN classifier on Kaggle-style B/W ISL images.

Expected structure:

    kaggle_dataset/
      a/
        img1.png
        img2.png
      b/
        ...

Usage:
    python -m src.train_cnn --root kaggle_dataset --model-path models/isl_cnn.h5
"""
from __future__ import annotations

import argparse
from pathlib import Path

import tensorflow as tf
from sklearn.metrics import classification_report

from src import config
from src.models.cnn_classifier import build_cnn
from src.utils.image_data_utils import load_image_dataset, train_val_split_images
from src.utils.data_utils import save_label_map


def train_cnn(root: Path, model_path: Path):
    X, y, idx_to_label = load_image_dataset(root)
    X_train, X_val, y_train, y_val = train_val_split_images(X, y)

    model = build_cnn(num_classes=len(idx_to_label))
    callbacks = [
        tf.keras.callbacks.ModelCheckpoint(
            filepath=str(model_path),
            monitor="val_accuracy",
            save_best_only=True,
            verbose=1,
        ),
        tf.keras.callbacks.EarlyStopping(
            monitor="val_accuracy", patience=8, restore_best_weights=True
        ),
    ]

    history = model.fit(
        X_train,
        y_train,
        validation_data=(X_val, y_val),
        epochs=config.EPOCHS,
        batch_size=config.BATCH_SIZE,
        shuffle=True,
        verbose=1,
        callbacks=callbacks,
    )

    val_probs = model.predict(X_val)
    val_preds = val_probs.argmax(axis=1)
    print(
        classification_report(
            y_val, val_preds, target_names=[idx_to_label[i] for i in sorted(idx_to_label)]
        )
    )

    # Save label map (reuses same filename as LSTM, but derived from CNN labels)
    save_label_map(idx_to_label)
    print(f"Saved CNN label map to {config.MODEL_DIR / 'label_map.json'}")
    return history


def parse_args():
    parser = argparse.ArgumentParser(description="Train CNN on B/W ISL Kaggle images.")
    parser.add_argument(
        "--root",
        type=Path,
        default=config.KAGGLE_IMAGE_DIR,
        help="Root folder of Kaggle image dataset.",
    )
    parser.add_argument(
        "--model-path",
        type=Path,
        default=config.MODEL_DIR / "isl_cnn.h5",
        help="Where to save the CNN model.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    config.MODEL_DIR.mkdir(parents=True, exist_ok=True)
    train_cnn(args.root, args.model_path)


