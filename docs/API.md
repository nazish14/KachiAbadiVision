# API documentation

FastAPI interactive docs: `/docs`; OpenAPI schema: `/openapi.json`.

- `GET /health`
- `POST /api/v1/detect`: multipart `file` required, optional `latitude`, `longitude`, `address`
- `GET /api/v1/reports?limit=50`
- `GET /api/v1/reports/{report_id}`
- `GET /api/v1/reports/{report_id}/json`
- `GET /api/v1/reports/{report_id}/annotated`
- `PATCH /api/v1/reports/{report_id}/status?status=Resolved`
- `GET /api/v1/map-points`

Allowed statuses: `Pending`, `In Progress`, `Resolved`. The detector expects the four category names documented in the README.
