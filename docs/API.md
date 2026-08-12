# API

Base URL: `http://localhost:3000`

All JSON responses use `{success, data, message}` on success and `{success:false,error:{code,message}}` on failure.

- `GET /health`
- `POST /api/auth/demo` with `{name,email,role}` returns a local demo bearer token.
- `GET /api/complaints?page=1&limit=20&search=&category=&priority=&status=&ward=`
- `POST /api/complaints` with `title`, `description`, and optional category/location/coordinates/ward.
- `GET|PATCH|DELETE /api/complaints/:id`
- `POST /api/complaints/:id/analyze` (idempotent)
- `GET /api/complaints/:id/related`
- `GET /api/systemic-issues`, `/api/departments`, `/api/notifications`
- `GET /api/analytics`
- `GET /api/map-data`

Use `Authorization: Bearer <token>` for authenticated integration. The current static Stitch pages contain no API client; they are preserved unchanged and can call these endpoints directly.
