"""Annotate an image using a detections JSON file."""
import argparse, json, sys
from pathlib import Path
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.services.annotate import annotate

parser = argparse.ArgumentParser()
parser.add_argument("image")
parser.add_argument("detections_json")
parser.add_argument("--output", default="annotated.jpg")
args = parser.parse_args()
data = json.loads(Path(args.detections_json).read_text(encoding="utf-8"))
Path(args.output).write_bytes(annotate(Image.open(args.image), data["detections"]))
print(f"Saved {args.output}")
