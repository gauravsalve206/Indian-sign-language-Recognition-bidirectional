"""
Train LSTM gesture classifier on MediaPipe landmark sequences.

Usage:
    python -m src.train
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import tensorflow as tf
from sklearn.metrics import classification_report

from src import config
from src.models.lstm_classifier import build_model
from src.utils import data_utils


def train(model_path: Path):
    X, y, idx_to_label = data_utils.load_dataset()
    if len(X) == 0:
        raise SystemExit("Dataset is empty. Collect data first.")

    # Print dataset statistics
    from collections import Counter
    label_counts = Counter(y)
    print("\n=== Dataset Statistics ===")
    for idx, label in sorted(idx_to_label.items()):
        count = label_counts.get(idx, 0)
        print(f"  {label}: {count} samples")
    print(f"Total: {len(X)} samples\n")

    X_train, X_val, y_train, y_val = data_utils.train_val_split(X, y)

    # Calculate class weights to handle imbalance
    from sklearn.utils.class_weight import compute_class_weight
    classes = np.unique(y_train)
    class_weights = compute_class_weight(
        'balanced', classes=classes, y=y_train
    )
    class_weight_dict = {int(cls): weight for cls, weight in zip(classes, class_weights)}
    print(f"Class weights: {class_weight_dict}\n")

    model = build_model(num_classes=len(idx_to_label))
    callbacks = [
        tf.keras.callbacks.ModelCheckpoint(
            filepath=model_path,
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
        class_weight=class_weight_dict,  # Handle class imbalance
    )

    val_preds = model.predict(X_val).argmax(axis=1)
    print(classification_report(y_val, val_preds, target_names=list(idx_to_label.values())))

    # Save label map for inference
    data_utils.save_label_map(idx_to_label)
    print(f"Saved label map to {config.MODEL_DIR / 'label_map.json'}")
    return history


def parse_args():
    parser = argparse.ArgumentParser(description="Train ISL gesture model.")
    parser.add_argument(
        "--model-path",
        type=Path,
        default=config.MODEL_DIR / "isl_lstm.h5",
        help="Where to save the trained model.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    config.MODEL_DIR.mkdir(parents=True, exist_ok=True)
    train(args.model_path)


