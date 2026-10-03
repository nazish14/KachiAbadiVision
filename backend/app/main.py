import json
import os
import uuid
from collections import Counter
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import Response
from PIL import Image, UnidentifiedImageError

from app.database import get_report, init_db, list_reports, save_report, update_status
from app.schemas import Category, DetectResponse, Detection
from app.services.annotate import annotate
from app.services.detector import detect

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
app = FastAPI(title="KachiAbadiVision API", version="0.1.0",
              description="Civic issue detection MVP. Demo detections are synthetic.")
BASE_DIR = Path(__file__).resolve().parents[1]
UPLOAD_DIR = BASE_DIR / "uploads"
MAX_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", "10485760"))
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
VALID_STATUSES = {"Pending", "In Progress", "Resolved"}

@app.on_event("startup")
def startup():
    init_db()
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def severity_for(detections: list[Detection]) -> str:
    if any(d.category == Category.open_manhole for d in detections):
        return "High"
    if any(d.category == Category.pothole for d in detections):
        return "Medium"
    if detections:
        return "Low"
    return "None"

@app.get("/health")
def health():
    return {"status": "ok", "service": "KachiAbadiVision"}

@app.post("/api/v1/detect", response_model=DetectResponse)
async def detect_endpoint(
    file: UploadFile = File(...),
    latitude: Optional[float] = Form(None, ge=-90, le=90),
    longitude: Optional[float] = Form(None, ge=-180, le=180),
    address: Optional[str] = Form(None, max_length=300),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(415, "Upload a JPEG, PNG, or WebP image.")
    raw = await file.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise HTTPException(413, "Image exceeds the configured upload limit.")
    if not raw:
        raise HTTPException(400, "The uploaded image is empty.")
    try:
        image = Image.open(BytesIO(raw))
        image.verify()
        image = Image.open(BytesIO(raw)).convert("RGB")
    except (UnidentifiedImageError, OSError, ValueError):
        raise HTTPException(400, "The uploaded file is not a valid image.")
    try:
        detections, demo_mode = detect(image)
    except RuntimeError as exc:
        raise HTTPException(503, str(exc))
    counts = dict(Counter(d.category.value for d in detections))
    report_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    image_path = UPLOAD_DIR / f"{report_id}.jpg"
    image.save(image_path, format="JPEG", quality=90)
    annotated = annotate(image, [d.model_dump(mode="json") for d in detections])
    (UPLOAD_DIR / f"{report_id}_annotated.jpg").write_bytes(annotated)
    report = {
        "id": report_id, "created_at": created_at,
        "image_path": str(image_path.relative_to(BASE_DIR)),
        "latitude": latitude, "longitude": longitude, "address": address,
        "status": "Pending", "severity": severity_for(detections),
        "demo_mode": demo_mode, "image_width": image.width,
        "image_height": image.height, "counts": counts
    }
    save_report(report, [d.model_dump(mode="json") for d in detections])
    return DetectResponse(
        report_id=report_id, image_width=image.width, image_height=image.height,
        detections=detections, counts=counts, severity=report["severity"],
        demo_mode=demo_mode, latitude=latitude, longitude=longitude,
        annotated_image_url=f"/api/v1/reports/{report_id}/annotated"
    )

@app.get("/api/v1/reports")
def reports(limit: int = Query(50, ge=1, le=200)):
    return [{
        "id": r["id"], "created_at": r["created_at"], "status": r["status"],
        "severity": r["severity"], "latitude": r["latitude"],
        "longitude": r["longitude"], "counts": r["counts"],
        "demo_mode": r["demo_mode"]
    } for r in list_reports(limit)]

@app.get("/api/v1/reports/{report_id}")
def report_detail(report_id: str):
    report = get_report(report_id)
    if report is None:
        raise HTTPException(404, "Report not found.")
    report.pop("image_path", None)
    return report

@app.get("/api/v1/reports/{report_id}/json")
def report_json(report_id: str):
    report = get_report(report_id)
    if report is None:
        raise HTTPException(404, "Report not found.")
    report.pop("image_path", None)
    return Response(
        content=json.dumps(report, indent=2), media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="report-{report_id}.json"'}
    )

@app.get("/api/v1/reports/{report_id}/annotated")
def annotated_image(report_id: str):
    if get_report(report_id) is None:
        raise HTTPException(404, "Report not found.")
    path = UPLOAD_DIR / f"{report_id}_annotated.jpg"
    if not path.exists():
        raise HTTPException(404, "Annotated image is unavailable.")
    return Response(path.read_bytes(), media_type="image/jpeg")

@app.patch("/api/v1/reports/{report_id}/status")
def set_report_status(report_id: str, status: str = Query(...)):
    if status not in VALID_STATUSES:
        raise HTTPException(422, f"Status must be one of {sorted(VALID_STATUSES)}")
    timestamp = datetime.now(timezone.utc).isoformat()
    if not update_status(report_id, status, timestamp):
        raise HTTPException(404, "Report not found.")
    return {"report_id": report_id, "status": status}

@app.get("/api/v1/map-points")
def map_points():
    return [{
        "id": r["id"], "latitude": r["latitude"], "longitude": r["longitude"],
        "severity": r["severity"], "status": r["status"],
        "created_at": r["created_at"], "counts": r["counts"]
    } for r in list_reports(200) if r["latitude"] is not None and r["longitude"] is not None]
