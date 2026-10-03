import json
import os
import sqlite3
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = Path(os.getenv("DATABASE_PATH", "data/kachiabadi.db"))
if not DB_PATH.is_absolute():
    DB_PATH = BASE_DIR / DB_PATH

def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with connect() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS reports (
            id TEXT PRIMARY KEY, created_at TEXT NOT NULL, image_path TEXT,
            latitude REAL, longitude REAL, address TEXT,
            status TEXT NOT NULL DEFAULT 'Pending', severity TEXT NOT NULL,
            demo_mode INTEGER NOT NULL DEFAULT 1, image_width INTEGER NOT NULL,
            image_height INTEGER NOT NULL, counts_json TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id TEXT NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
            category TEXT NOT NULL, confidence REAL NOT NULL,
            x1 REAL NOT NULL, y1 REAL NOT NULL, x2 REAL NOT NULL, y2 REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS report_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id TEXT NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
            old_status TEXT, new_status TEXT NOT NULL, created_at TEXT NOT NULL
        );
        """)

def save_report(report: dict[str, Any], detections: list[dict[str, Any]]):
    with connect() as conn:
        conn.execute("""INSERT INTO reports
        (id, created_at, image_path, latitude, longitude, address, status, severity,
         demo_mode, image_width, image_height, counts_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
            report["id"], report["created_at"], report.get("image_path"),
            report.get("latitude"), report.get("longitude"), report.get("address"),
            report["status"], report["severity"], int(report["demo_mode"]),
            report["image_width"], report["image_height"], json.dumps(report["counts"])
        ))
        conn.executemany("""INSERT INTO detections
        (report_id, category, confidence, x1, y1, x2, y2) VALUES (?, ?, ?, ?, ?, ?, ?)""",
        [(report["id"], d["category"], d["confidence"], *d["bbox"]) for d in detections])
        conn.execute(
            "INSERT INTO report_events (report_id, old_status, new_status, created_at) VALUES (?, ?, ?, ?)",
            (report["id"], None, "Pending", report["created_at"])
        )

def get_report(report_id: str):
    with connect() as conn:
        row = conn.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
        if row is None:
            return None
        report = dict(row)
        report["counts"] = json.loads(report.pop("counts_json"))
        report["demo_mode"] = bool(report["demo_mode"])
        rows = conn.execute(
            "SELECT category, confidence, x1, y1, x2, y2 FROM detections WHERE report_id = ?",
            (report_id,)
        ).fetchall()
        report["detections"] = [
            {"category": r["category"], "confidence": r["confidence],
             "bbox": [r["x1"], r["y1"], r["x2"], r["y2"]]} for r in rows
        ]
        return report

def list_reports(limit: int = 50):
    with connect() as conn:
        rows = conn.execute("SELECT * FROM reports ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            item["counts"] = json.loads(item.pop("counts_json"))
            item["demo_mode"] = bool(item["demo_mode"])
            result.append(item)
        return result

def update_status(report_id: str, status: str, timestamp: str) -> bool:
    with connect() as conn:
        row = conn.execute("SELECT status FROM reports WHERE id = ?", (report_id,)).fetchone()
        if row is None:
            return False
        conn.execute("UPDATE reports SET status = ? WHERE id = ?", (status, report_id))
        conn.execute(
            "INSERT INTO report_events (report_id, old_status, new_status, created_at) VALUES (?, ?, ?, ?)",
            (report_id, row["status"], status, timestamp)
        )
        return True
