from __future__ import annotations

import cv2
import mediapipe as mp
import numpy as np
from typing import Optional, Tuple, List

from src import config


mp_hands = mp.solutions.hands
mp_face_mesh = mp.solutions.face_mesh
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles


def create_hand_tracker(static_image_mode: bool = False, max_num_hands: int = 2):
    return mp_hands.Hands(
        static_image_mode=static_image_mode,
        max_num_hands=max_num_hands,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )


def create_face_tracker(static_image_mode: bool = False):
    return mp_face_mesh.FaceMesh(
        static_image_mode=static_image_mode,
        max_num_faces=1,
        refine_landmarks=True,  # Get more detailed landmarks
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )


def create_pose_tracker(static_image_mode: bool = False):
    return mp_pose.Pose(
        static_image_mode=static_image_mode,
        model_complexity=1,  # 0=fast, 1=balanced, 2=accurate
        enable_segmentation=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )


def extract_face_landmarks(
    image: np.ndarray,
    face_mesh: mp_face_mesh.FaceMesh,
    draw: bool = False,
) -> Optional[np.ndarray]:
    """
    Extract face landmarks from MediaPipe Face Mesh (468 landmarks * 3 = 1404 values).
    Returns None if no face detected.
    """
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    if not results.multi_face_landmarks:
        return None

    # Get the first (and only) face
    face_landmarks = results.multi_face_landmarks[0]
    
    if draw:
        mp_drawing.draw_landmarks(
            image,
            face_landmarks,
            mp_face_mesh.FACEMESH_CONTOURS,
            None,
            mp_drawing_styles.get_default_face_mesh_contours_style(),
        )

    # Extract all 468 landmarks (x, y, z)
    coords = [[lm.x, lm.y, lm.z] for lm in face_landmarks.landmark]
    landmarks = np.array(coords, dtype=np.float32).flatten()
    return landmarks


def extract_hand_landmarks(
    image: np.ndarray,
    hands: mp_hands.Hands,
    draw: bool = False,
) -> Optional[np.ndarray]:
    """
    Return flattened landmarks for up to TWO hands (2 * 21 * 3 = 126 values).
    If only one hand is visible, the second hand is zero-padded.
    """
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if not results.multi_hand_landmarks:
        return None

    # Pair handedness with landmarks so we can keep a consistent ordering
    hands_list: List = list(results.multi_hand_landmarks)
    handedness_list: List = list(getattr(results, "multi_handedness", []))

    pairs = list(zip(handedness_list, hands_list)) if handedness_list else [(None, h) for h in hands_list]

    # Sort so index 0 is always "Left", index 1 is "Right" when available
    def sort_key(item):
        h, _ = item
        if h is None:
            return 2
        label = h.classification[0].label
        return 0 if label.lower() == "left" else 1

    pairs.sort(key=sort_key)

    all_coords = []
    drawn = 0
    for i in range(2):
        if i < len(pairs):
            h_info, h_landmarks = pairs[i]
            if draw:
                mp_drawing.draw_landmarks(image, h_landmarks, mp_hands.HAND_CONNECTIONS)
            coords = [[lm.x, lm.y, lm.z] for lm in h_landmarks.landmark]
            drawn += 1
        else:
            # No second hand: pad with zeros (21 landmarks)
            coords = [[0.0, 0.0, 0.0] for _ in range(21)]
        all_coords.extend(coords)

    landmarks = np.array(all_coords, dtype=np.float32).flatten()
    return landmarks


def extract_pose_upper_body_landmarks(
    image: np.ndarray,
    pose: mp_pose.Pose,
    draw: bool = False,
) -> Optional[np.ndarray]:
    """
    Extract upper body pose landmarks relevant for ISL (head, chest, shoulders, arms).
    MediaPipe Pose has 33 landmarks. We extract 11 key upper body points:
    - 0: nose (head)
    - 2, 5: left/right eye (head)
    - 7, 8: left/right ear (head)
    - 11, 12: left/right shoulder (chest region)
    - 13, 14: left/right elbow (arms)
    - 15, 16: left/right wrist (arms, connects to hands)
    
    Returns: 11 landmarks * 3 = 33 values, or None if no pose detected.
    """
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb)

    if not results.pose_landmarks:
        return None

    # Upper body key point indices for ISL
    UPPER_BODY_INDICES = [0, 2, 5, 7, 8, 11, 12, 13, 14, 15, 16]
    # 0=nose, 2=left_eye, 5=right_eye, 7=left_ear, 8=right_ear
    # 11=left_shoulder, 12=right_shoulder, 13=left_elbow, 14=right_elbow
    # 15=left_wrist, 16=right_wrist

    if draw:
        mp_drawing.draw_landmarks(
            image,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            mp_drawing_styles.get_default_pose_landmarks_style(),
        )

    # Extract only upper body landmarks
    pose_landmarks = results.pose_landmarks.landmark
    coords = []
    for idx in UPPER_BODY_INDICES:
        lm = pose_landmarks[idx]
        coords.append([lm.x, lm.y, lm.z])

    landmarks = np.array(coords, dtype=np.float32).flatten()
    return landmarks


def extract_combined_landmarks(
    image: np.ndarray,
    hands: mp_hands.Hands,
    face_mesh: mp_face_mesh.FaceMesh,
    pose: mp_pose.Pose,
    draw: bool = False,
) -> Optional[np.ndarray]:
    """
    Extract combined hand, face, and upper body pose landmarks for complete ISL signs.
    Returns: [hand_landmarks (126), face_landmarks (1404), pose_upper_body (33)] = 1563 values total.
    Returns None if no person is detected in the frame (requires pose detection as proof of person presence).
    """
    hand_lm = extract_hand_landmarks(image, hands, draw=draw)
    face_lm = extract_face_landmarks(image, face_mesh, draw=draw)
    pose_lm = extract_pose_upper_body_landmarks(image, pose, draw=draw)

    # Require pose detection to ensure there's actually a person in the frame
    # This prevents false positives from hands/face when no person is present
    if pose_lm is None:
        return None

    # Pad missing parts with zeros (hands and face are optional, pose is required)
    if hand_lm is None:
        hand_lm = np.zeros(126, dtype=np.float32)
    if face_lm is None:
        face_lm = np.zeros(1404, dtype=np.float32)

    # Combine: hands, face, then pose
    combined = np.concatenate([hand_lm, face_lm, pose_lm])
    
    # Ensure exact shape (safety check)
    expected_size = config.NUM_LANDMARKS
    if combined.shape[0] != expected_size:
        # Pad or truncate to exact size
        if combined.shape[0] < expected_size:
            combined = np.concatenate([combined, np.zeros(expected_size - combined.shape[0], dtype=np.float32)])
        else:
            combined = combined[:expected_size]
    
    return combined


def draw_info(frame: np.ndarray, text: str, color=(0, 255, 0)):
    cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)


def center_crop(frame: np.ndarray, size: Tuple[int, int] = (640, 480)) -> np.ndarray:
    h, w, _ = frame.shape
    target_w, target_h = size
    x0 = max((w - target_w) // 2, 0)
    y0 = max((h - target_h) // 2, 0)
    return frame[y0 : y0 + target_h, x0 : x0 + target_w]


