"""
FastAPI backend for ISL recognition.

Run:
    uvicorn src.server:app --reload --port 8000
"""
from __future__ import annotations

import base64
import json
import collections
from pathlib import Path
from typing import Deque, List

import cv2
import numpy as np
import tensorflow as tf
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from src import config
from src.utils.data_utils import load_label_map
from src.utils.mediapipe_utils import (
    create_hand_tracker,
    create_face_tracker,
    create_pose_tracker,
    extract_combined_landmarks,
)

# Get the frontend directory path
FRONTEND_DIR = config.PROJECT_ROOT / "frontend"

app = FastAPI(title="ISL Recognition API", version="1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files from frontend directory
app.mount("/static/frontend", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend_static")
# Serve text_to_sign GIFs
TEXT_TO_SIGN_DIR = config.PROJECT_ROOT / "text_to_sign"
if TEXT_TO_SIGN_DIR.exists():
    app.mount("/static/text_to_sign", StaticFiles(directory=str(TEXT_TO_SIGN_DIR)), name="text_to_sign_static")

model = tf.keras.models.load_model(config.MODEL_DIR / "isl_lstm.h5")
label_map = load_label_map()
# Track hands, face, AND upper body pose (chest, head, shoulders) for complete ISL signs
hands = create_hand_tracker(static_image_mode=False, max_num_hands=2)
face_mesh = create_face_tracker(static_image_mode=False)
pose = create_pose_tracker(static_image_mode=False)


class PredictRequest(BaseModel):
    # Length equals config.NUM_LANDMARKS (hands: 126 + face: 1404 + pose: 33 = 1563)
    landmarks: List[float]


class TextToSignRequest(BaseModel):
    text: str


@app.get("/")
async def read_root():
    """Serve the main landing page"""
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "ISL Recognition API", "version": "1.0"}


@app.get("/sign-to-text.html")
async def sign_to_text_page():
    """Serve the sign-to-text page"""
    page_path = FRONTEND_DIR / "sign-to-text.html"
    if page_path.exists():
        return FileResponse(page_path)
    return {"error": "Page not found"}


@app.get("/text-to-sign.html")
async def text_to_sign_page():
    """Serve the text-to-sign page"""
    page_path = FRONTEND_DIR / "text-to-sign.html"
    if page_path.exists():
        return FileResponse(page_path)
    return {"error": "Page not found"}


@app.get("/labels")
def get_labels():
    return {"labels": label_map}


@app.post("/predict")
def predict_landmarks(req: PredictRequest):
    if len(req.landmarks) != config.NUM_LANDMARKS:
        return {"error": f"Expected {config.NUM_LANDMARKS} values"}

    seq = np.array(req.landmarks, dtype=np.float32)[None, None, :]
    # Pad to full sequence length
    seq = np.tile(seq, (1, config.SEQUENCE_LENGTH, 1))
    probs = model.predict(seq, verbose=0)[0]
    idx = int(np.argmax(probs))
    return {"label": label_map.get(idx, "unknown"), "confidence": float(np.max(probs))}


@app.websocket("/ws")
async def websocket_predict(ws: WebSocket):
    await ws.accept()
    frame_buffer: Deque[np.ndarray] = collections.deque(maxlen=config.SEQUENCE_LENGTH)
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
            # Extract combined hand + face + pose (chest, head, upper body) landmarks
            landmarks = extract_combined_landmarks(frame, hands, face_mesh, pose)
            if landmarks is not None:
                frame_buffer.append(landmarks)

            if len(frame_buffer) == config.SEQUENCE_LENGTH:
                seq = np.expand_dims(np.array(frame_buffer), axis=0)
                probs = model.predict(seq, verbose=0)[0]
                idx = int(np.argmax(probs))
                conf = float(np.max(probs))
                await ws.send_json({"label": label_map.get(idx, "unknown"), "confidence": conf})
            else:
                await ws.send_json({"label": "collecting", "confidence": 0.0})
    except WebSocketDisconnect:
        return


@app.post("/text-to-sign")
async def text_to_sign(req: TextToSignRequest):
    """
    Convert text to Indian Sign Language GIF.
    Returns the path to the GIF file if found, or instructions for spelling.
    """
    import string
    
    # ISL GIF database - phrases that have GIF files
    isl_gif = [
        'any questions', 'are you angry', 'are you busy', 'are you hungry', 'are you sick', 'be careful',
        'can we meet tomorrow', 'did you book tickets', 'did you finish homework', 'do you go to office', 'do you have money',
        'do you want something to drink', 'do you want tea or coffee', 'do you watch TV', 'dont worry', 'flower is beautiful',
        'good afternoon', 'good evening', 'good morning', 'good night', 'good question', 'had your lunch', 'happy journey',
        'hello what is your name', 'how many people are there in your family', 'i am a clerk', 'i am bore doing nothing', 
        'i am fine', 'i am sorry', 'i am thinking', 'i am tired', 'i dont understand anything', 'i go to a theatre', 'i love to shop',
        'i had to say something but i forgot', 'i have headache', 'i like pink colour', 'i live in nagpur', 'lets go for lunch', 'my mother is a homemaker',
        'my name is john', 'nice to meet you', 'no smoking please', 'open the door', 'please call me later',
        'please clean the room', 'please give me your pen', 'please use dustbin dont throw garbage', 'please wait for sometime', 'shall I help you',
        'shall we go together tommorow', 'sign language interpreter', 'sit down', 'stand up', 'take care', 'there was traffic jam', 'wait I am thinking',
        'what are you doing', 'what is the problem', 'what is todays date', 'what is your father do', 'what is your job',
        'what is your mobile number', 'what is your name', 'whats up', 'when is your interview', 'when we will go', 'where do you stay',
        'where is the bathroom', 'where is the police station', 'you are wrong',
        'address', 'agra', 'ahemdabad','good night', 'all', 'april', 'assam', 'august', 'australia', 'badoda', 'banana', 'banaras', 'banglore',
        'bihar', 'bridge', 'cat', 'chandigarh', 'chennai', 'christmas', 'church', 'clinic', 'coconut', 'crocodile', 'dasara',
        'deaf', 'december', 'deer', 'delhi', 'dollar', 'duck', 'febuary', 'friday', 'fruits', 'glass', 'grapes', 'gujrat', 'hello',
        'hindu', 'hyderabad', 'india', 'january', 'jesus', 'job', 'july', 'karnataka', 'kerala', 'krishna', 'litre', 'mango',
        'may', 'mile', 'monday', 'mumbai', 'museum', 'muslim', 'nagpur', 'october', 'orange', 'pakistan', 'pass', 'police station',
        'post office', 'pune', 'punjab', 'rajasthan', 'ram', 'restaurant', 'saturday', 'september', 'shop', 'sleep', 'southafrica',
        'story', 'sunday', 'tamil nadu', 'temperature', 'temple', 'thursday', 'toilet', 'tomato', 'town', 'tuesday', 'usa', 'village',
        'voice', 'wednesday', 'weight'
    ]
    
    text = req.text.lower().strip()
    
    # Clean punctuation
    for c in string.punctuation:
        text = text.replace(c, "")
    
    # Check if text matches any phrase in the database
    # First check for exact match, then try longest phrases first (to avoid partial matches)
    matched_phrase = None
    
    # Check exact match first
    if text in isl_gif:
        matched_phrase = text
    else:
        # Sort by length (longest first) to match longer phrases before shorter ones
        sorted_phrases = sorted(isl_gif, key=len, reverse=True)
        for phrase in sorted_phrases:
            # Check if text contains the phrase or phrase contains text
            if phrase in text or text in phrase:
                matched_phrase = phrase
                break
    
    # Check if GIF file exists
    if matched_phrase:
        gif_path = config.PROJECT_ROOT / "text_to_sign" / "ISL_Gifs" / f"{matched_phrase}.gif"
        if gif_path.exists():
            # Return relative path from project root
            relative_path = f"/static/text_to_sign/ISL_Gifs/{matched_phrase}.gif"
            return {
                "text": req.text,
                "matched_phrase": matched_phrase,
                "status": "success",
                "type": "gif",
                "gif_path": relative_path,
                "message": f"Found sign language GIF for: {matched_phrase}"
            }
    
    # If no match found, return spelling instructions with letter paths
    alphabet = list('abcdefghijklmnopqrstuvwxyz')
    letters = [c for c in text if c.lower() in alphabet]
    
    # Check which format is available for each letter (GIF preferred, fallback to JPG)
    letter_paths = []
    for letter in letters:
        letter_lower = letter.lower()
        # Check for GIF first, then JPG
        gif_path = config.PROJECT_ROOT / "text_to_sign" / "ISL_Gifs" / f"{letter_lower}.gif"
        jpg_path = config.PROJECT_ROOT / "text_to_sign" / "ISL_Gifs" / f"{letter_lower}.jpg"
        
        if gif_path.exists():
            letter_paths.append({
                "letter": letter,
                "path": f"/static/text_to_sign/ISL_Gifs/{letter_lower}.gif",
                "format": "gif"
            })
        elif jpg_path.exists():
            letter_paths.append({
                "letter": letter,
                "path": f"/static/text_to_sign/ISL_Gifs/{letter_lower}.jpg",
                "format": "jpg"
            })
        else:
            letter_paths.append({
                "letter": letter,
                "path": None,
                "format": None
            })
    
    return {
        "text": req.text,
        "status": "spell",
        "type": "letters",
        "letters": letter_paths,
        "message": f"No GIF found. Will spell out: {text}"
    }

