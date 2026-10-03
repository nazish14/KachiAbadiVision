# Deployment notes

Before public deployment:
- Use HTTPS, authentication, authorization, rate limiting, and audit logs.
- Use PostgreSQL/PostGIS and managed object storage for production.
- Configure restricted CORS origins, backups, monitoring, and migrations.
- Set upload limits and validate decoded image dimensions.
- Define retention/deletion policies for uploaded images and location data.
- Store secrets in the platform secret manager; never commit `.env` or API keys.
- Train and validate a model on representative, properly licensed data.
- Configure Google Maps keys with platform restrictions before enabling map SDKs.

Current limitations: mobile UI is a starter and does not yet contain a map screen, PDF export, authentication, video processing, or in-app bounding-box overlay. The backend creates annotated images and JSON reports. Demo detections are synthetic.
