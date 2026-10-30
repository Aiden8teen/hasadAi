"""Configuration, Google AI Studio settings, and model drop-in paths for Hassad AI."""
import os
from pathlib import Path

# Root project directories
BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent
MODELS_DIR = PROJECT_ROOT / "models"
WEB_DIR = PROJECT_ROOT / "web"
EVAL_PLOTS_DIR = WEB_DIR / "eval_plots"
DATA_DIR = BACKEND_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
MASKS_DIR = DATA_DIR / "masks"
DB_PATH = DATA_DIR / "hassad.db"
ENV_FILE = BACKEND_DIR / ".env"

for d in (MODELS_DIR, WEB_DIR, EVAL_PLOTS_DIR, DATA_DIR, UPLOADS_DIR, MASKS_DIR):
    d.mkdir(parents=True, exist_ok=True)


def load_env_file() -> None:
    """Loads key=value pairs from backend/.env without requiring python-dotenv."""
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


load_env_file()

GOOGLE_API_KEY = os.environ.get(
    "GOOGLE_API_KEY",
    "AQ.Ab8RN6JIWKTAHWCDWsLBgoZEREb4TXNzoT0LVjVVQA03LTc4SQ",
)
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

# Expected drop-in model files in /models (Prioritize lightweight TFLite and ONNX runtimes for < 512MB RAM cloud hosting)
EFFICIENTNET_CANDIDATES = [
    MODELS_DIR / "plant_disease_efficientnet_fp16.tflite",
    MODELS_DIR / "best_plant_efficientnet.keras",
    MODELS_DIR / "plant_disease_efficientnet_head_only.keras",
    MODELS_DIR / "best_plant_efficientnet.h5",
]

YOLO_CANDIDATES = [
    MODELS_DIR / "best.onnx",
    MODELS_DIR / "best.pt",
    MODELS_DIR / "yolov9e-seg.pt",
]

UNET_CANDIDATES = [
    MODELS_DIR / "unet_leaf_aug_best.onnx",
    MODELS_DIR / "unet_leaf_aug_best.keras",
    MODELS_DIR / "unet_leaf_aug_best.h5",
]

PHI2_LORA_ZIP = MODELS_DIR / "disease_rec_phi2_lora.zip"
PHI2_LORA_DIR = MODELS_DIR / "disease_rec_phi2_lora"
TAXONOMY_JSON_PATH = MODELS_DIR / "class_taxonomy.json"
KB_JSON_PATH = MODELS_DIR / "disease_recommendations_kb.json"

# Decision thresholds (per Architecture Review & PRD v2.1)
CROP_CONFIDENCE_THRESHOLD = 0.80      # >= 0.80 auto-routes to Stage 2; < 0.80 asks farmer to confirm crop
DISEASE_AUTO_THRESHOLD = 0.75         # >= 0.75 auto-verified diagnosis
DISEASE_REVIEW_THRESHOLD = 0.50       # 0.50 - 0.75 flagged needs_review for agronomist queue
MIN_LEAF_MASK_PCT = 0.5               # Minimum plausible lesion area % on a diseased leaf
MAX_LEAF_MASK_PCT = 92.0              # Maximum plausible lesion area % before background leak rejection
