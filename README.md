# KachiAbadiVision

AI-assisted civic issue reporting MVP for garbage dumps, potholes, open manholes, and damaged streetlights.

## Included
- Expo / React Native TypeScript mobile starter (camera, gallery upload, optional GPS)
- FastAPI backend: detection, reports, map-points, annotated images, JSON exports
- SQLite persistence
- Optional YOLO inference (trained weights are not included)
- Clearly labelled synthetic demo mode

> Demo detections are synthetic and must not be treated as real findings. Real AI inference requires a compatible trained model at `ai_model/best.pt`.

## Requirements
- Python 3.10+
- Node.js 18+
- Expo Go or simulator

## Run backend
```bash
cd backend
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Open http://127.0.0.1:8000/docs

Set `DEMO_MODE=true` in `backend/.env` for synthetic demo results (default). Set `DEMO_MODE=false` and provide a trained `ai_model/best.pt` to use YOLO. Expected class names: `garbage_dump`, `pothole`, `open_manhole`, `damaged_lights`.

## Run mobile app
```bash
cd mobile
npm install
npx expo start
```
Configure `EXPO_PUBLIC_API_URL`:
- Android emulator: `http://10.0.2.2:8000`
- iOS simulator: `http://127.0.0.1:8000`
- Physical phone: `http://YOUR_COMPUTER_LAN_IP:8000`

## Publish to GitHub
1. Extract the ZIP.
2. Create a new empty GitHub repository.
3. Open a terminal in this folder and run:
```bash
git init
git add .
git commit -m "Initial KachiAbadiVision MVP"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/KachiAbadiVision.git
git push -u origin main
```
Do not commit secrets, real user images, personal location data, `.env` files, or model weights.

## API
- `GET /health`
- `POST /api/v1/detect`
- `GET /api/v1/reports`
- `GET /api/v1/reports/{report_id}`
- `GET /api/v1/reports/{report_id}/json`
- `GET /api/v1/reports/{report_id}/annotated`
- `PATCH /api/v1/reports/{report_id}/status?status=Resolved`
- `GET /api/v1/map-points`

Interactive API docs: `/docs`.
