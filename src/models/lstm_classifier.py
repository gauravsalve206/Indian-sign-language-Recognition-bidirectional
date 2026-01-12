from __future__ import annotations

import tensorflow as tf
from tensorflow.keras import layers, models

from src import config


def build_model(num_classes: int) -> tf.keras.Model:
    model = models.Sequential(
        [
            layers.Input(shape=(config.SEQUENCE_LENGTH, config.NUM_LANDMARKS)),
            layers.Masking(mask_value=0.0),
            layers.LSTM(128, return_sequences=True),
            layers.Dropout(0.3),
            layers.LSTM(64),
            layers.Dropout(0.3),
            layers.Dense(64, activation="relu"),
            layers.Dropout(0.2),
            layers.Dense(num_classes, activation="softmax"),
        ]
    )

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=config.LEARNING_RATE),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


