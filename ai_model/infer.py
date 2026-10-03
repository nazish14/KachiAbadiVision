"""CLI inference helper; requires a trained ai_model/best.pt and backend dependencies."""
import argparse, json, os, sys
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.services.detector import yolo_detect

parser = argparse.ArgumentParser()
parser.add_argument("image")
parser.add_argument("--output", default="detections.json")
args = parser.parse_args()
image = Image.open(args.image).convert("RGB")
detections = yolo_detect(image)
payload = {"image": args.image, "width": image.width, "height": image.height,
           "detections": [d.model_dump(mode="json") for d in detections]}
Path(args.output).write_text(json.dumps(payload, indent=2), encoding="utf-8")
print(f"Wrote {len(detections)} detections to {args.output}")
