# JAN-SHIELD AI Architecture

The backend is a dependency-free Python standard-library service for a reliable zero-cost local demo. SQLite is used locally and the schema is explicit in `backend/schema.sql`; the persistence boundary can later be replaced by PostgreSQL without changing API contracts.

## Workflow

Complaint creation stores the citizen report first. The analysis endpoint then executes structured modules in order: complaint understanding, evidence capability reporting, related-complaint metadata matching, deterministic priority scoring, cluster/systemic-issue detection, recommendation, and database-backed notification. Demo analysis is clearly deterministic and is not presented as a real LLM decision.

## Safety

Status changes are server-side guarded. AI output is an assessment/recommendation only. Administrative action remains human-approved. Tokens are signed with `AUTH_SECRET`; use a real secret outside local demos. Uploaded evidence should be stored behind a validated upload service before production deployment.

## Data

The schema includes users, complaints, evidence, AI analyses, clusters, systemic issues, departments, resolutions, notifications, and audit logs. All IDs are opaque UUID-style values and all timestamps are UTC ISO-8601 strings.
