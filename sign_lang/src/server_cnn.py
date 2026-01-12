"""
FastAPI backend for ISL recognition using CNN on B/W images (no MediaPipe).

Run:
    uvicorn src.server_cnn:app --reload --port 8000
"""
from __future__ import annotations

import base64
import json
from typing import List

import cv2
import numpy as np
import tensorflow as tf
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src import config
from src.utils.data_utils import load_label_map


app = FastAPI(title="ISL CNN Recognition API", version="1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = tf.keras.models.load_model(config.MODEL_DIR / "isl_cnn.h5")
label_map = load_label_map()


def preprocess_frame(frame: np.ndarray) -> np.ndarray:
    """BGR frame -> (1, H, W, 1) grayscale, binarized, normalized."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, (config.IMAGE_SIZE, config.IMAGE_SIZE))
    _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    bw = bw.astype("float32") / 255.0
    bw = np.expand_dims(bw, axis=-1)
    bw = np.expand_dims(bw, axis=0)
    return bw


class PredictImageRequest(BaseModel):
    image_base64: str  # data URL or raw base64 of JPEG/PNG frame


@app.get("/labels")
def get_labels():
    return {"labels": label_map}


@app.post("/predict_image")
def predict_image(req: PredictImageRequest):
    img_b64 = req.image_base64
    img_bytes = base64.b64decode(img_b64.split(",")[-1])
    img_arr = np.frombuffer(img_bytes, dtype=np.uint8)
    frame = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
    if frame is None:
        return {"error": "Could not decode image"}

    inp = preprocess_frame(frame)
    probs = model.predict(inp, verbose=0)[0]
    idx = int(np.argmax(probs))
    return {"label": label_map.get(idx, "unknown"), "confidence": float(np.max(probs))}


@app.websocket("/ws")
async def websocket_predict(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            data = await ws.receive_text()
            payload = json.loads(data)
            image_b64 = payload.get("image")
            if not image_b64:
                continue
            img_bytes = base64.b64decode(image_b64.split(",")[-1])
            image_array = np.frombuffer(img_bytes, dtype=np.uint8)
            frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            if frame is None:
                await ws.send_json({"label": "error", "confidence": 0.0})
                continue

            inp = preprocess_frame(frame)
            probs = model.predict(inp, verbose=0)[0]
            idx = int(np.argmax(probs))
            conf = float(np.max(probs))
            await ws.send_json({"label": label_map.get(idx, "unknown"), "confidence": conf})
    except WebSocketDisconnect:
        return


