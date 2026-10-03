import os
import random
from pathlib import Path
from PIL import Image
from app.schemas import Category, Detection

CATEGORIES = list(Category)

def demo_detect(image: Image.Image) -> list[Detection]:
    # Synthetic detections only, intended for UI demonstration.
    rng = random.Random(image.width * 1009 + image.height * 9176)
    if image.width < 80 or image.height < 80:
        return []
    results = []
    for _ in range(rng.randint(0, 3)):
        x1, y1 = rng.uniform(.05, .55), rng.uniform(.05, .55)
        x2, y2 = min(.98, x1 + rng.uniform(.12, .28)), min(.98, y1 + rng.uniform(.12, .28))
        results.append(Detection(
            category=rng.choice(CATEGORIES), confidence=round(rng.uniform(.72, .96), 2),
            bbox=[round(x1, 4), round(y1, 4), round(x2, 4), round(y2, 4)]
        ))
    return results

def yolo_detect(image: Image.Image) -> list[Detection]:
    model_path = os.getenv("YOLO_MODEL_PATH") or str(Path(__file__).resolve().parents[3] / "ai_model" / "best.pt")
    if not Path(model_path).exists():
        raise RuntimeError(f"YOLO weights not found at {model_path}. Add a trained model or enable DEMO_MODE.")
    from ultralytics import YOLO
    model = YOLO(model_path)
    predictions = model.predict(image, conf=float(os.getenv("YOLO_CONFIDENCE", ".35")), verbose=False)
    results = []
    width, height = image.size
    for prediction in predictions:
        if prediction.boxes is None:
            continue
        for box in prediction.boxes:
            name = str(prediction.names[int(box.cls.item())]).strip().lower()
            try:
                category = Category(name)
            except ValueError:
                continue
            x1, y1, x2, y2 = [float(v) for v in box.xyxy[0].tolist()]
            results.append(Detection(
                category=category, confidence=float(box.conf.item()),
                bbox=[max(0, min(1, x1 / width)), max(0, min(1, y1 / height)),
                      max(0, min(1, x2 / width)), max(0, min(1, y2 / height))]
            ))
    return results

def detect(image: Image.Image):
    if os.getenv("DEMO_MODE", "true").lower() == "true":
        return demo_detect(image), True
    return yolo_detect(image), False
