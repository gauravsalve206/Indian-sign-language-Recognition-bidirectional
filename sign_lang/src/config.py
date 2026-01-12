import pathlib

# Base paths
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "dataset"
MODEL_DIR = PROJECT_ROOT / "models"
KAGGLE_IMAGE_DIR = PROJECT_ROOT / "kaggle_dataset"

# Data/Model parameters (LSTM landmark model)
SEQUENCE_LENGTH = 30  # frames per sample
# Hands: 2 hands * 21 landmarks * (x, y, z) = 126
# Face: MediaPipe Face Mesh has 468 landmarks * (x, y, z) = 1404
# Pose (upper body): MediaPipe Pose has 33 landmarks, we use upper body subset (11 key points) = 33
#   Key points: nose, eyes, ears, shoulders, elbows, wrists, chest region
# Total: 126 + 1404 + 33 = 1563 features per frame
HAND_LANDMARKS = 2 * 21 * 3  # 126
FACE_LANDMARKS = 468 * 3  # 1404 (MediaPipe Face Mesh)
POSE_UPPER_BODY_LANDMARKS = 11 * 3  # 33 (head, shoulders, chest, arms)
NUM_LANDMARKS = HAND_LANDMARKS + FACE_LANDMARKS + POSE_UPPER_BODY_LANDMARKS  # 1563

# Data/Model parameters (CNN image model)
IMAGE_SIZE = 128  # H = W
IMAGE_CHANNELS = 1  # grayscale for B/W Kaggle images
TEST_SPLIT = 0.2
RANDOM_STATE = 42

# Training parameters
BATCH_SIZE = 32
EPOCHS = 50
LEARNING_RATE = 1e-3
MIN_CONFIDENCE = 0.6  # threshold for predictions in inference


