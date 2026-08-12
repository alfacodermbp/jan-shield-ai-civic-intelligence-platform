# Local Setup

Requirements: Python 3.10+ and Node.js only if using the existing static preview. No paid service, database server, or Python package is required.

```bash
cp .env.example .env
python3 -m backend.seed
PORT=3000 python3 -m backend.app
```

In another terminal:

```bash
python3 -m unittest discover -s backend/tests -p 'test_*.py' -v
npx --yes serve stitch_jan_shield_ai_civic_intelligence_platform --listen 3001
```

The SQLite database is created at `backend/data/janshield.db` by default. To reset demo data, remove that file and rerun the seed command. Set `DATABASE_PATH` to use another local file. PostgreSQL is intentionally not forced into this repository so the existing zero-cost/local configuration remains intact.
