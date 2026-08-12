from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import re
import sqlite3
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("DATABASE_PATH", ROOT / "data" / "janshield.db"))
SECRET = os.getenv("AUTH_SECRET", "local-demo-secret-change-me")
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
log = logging.getLogger("janshield")

SCHEMA = (ROOT / "schema.sql").read_text()
STATUSES = ["SUBMITTED", "AI_ANALYZING", "AI_ANALYZED", "ASSIGNED", "ACTION_INITIATED", "IN_PROGRESS", "RESOLUTION_PENDING_VERIFICATION", "RESOLVED", "REOPENED", "REJECTED"]
TRANSITIONS = {
    "SUBMITTED": {"AI_ANALYZING", "REJECTED"}, "AI_ANALYZING": {"AI_ANALYZED", "SUBMITTED"},
    "AI_ANALYZED": {"ASSIGNED", "REJECTED"}, "ASSIGNED": {"ACTION_INITIATED", "IN_PROGRESS"},
    "ACTION_INITIATED": {"IN_PROGRESS", "RESOLUTION_PENDING_VERIFICATION"}, "IN_PROGRESS": {"RESOLUTION_PENDING_VERIFICATION"},
    "RESOLUTION_PENDING_VERIFICATION": {"RESOLVED", "REOPENED"}, "REOPENED": {"ASSIGNED", "IN_PROGRESS"},
    "RESOLVED": {"REOPENED"}, "REJECTED": set()
}

def now(): return datetime.now(timezone.utc).isoformat()
def conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB_PATH); c.row_factory = sqlite3.Row; c.execute("PRAGMA foreign_keys=ON"); return c
def init_db():
    with conn() as c: c.executescript(SCHEMA)
def uid(prefix=""): return prefix + str(uuid.uuid4())
def rows(c, sql, args=()): return [dict(r) for r in c.execute(sql, args).fetchall()]
def one(c, sql, args=()):
    r = c.execute(sql, args).fetchone(); return dict(r) if r else None
def ok(data, message="Operation completed successfully", status=200): return status, {"success": True, "data": data, "message": message}
def err(code, message, status=400): return status, {"success": False, "error": {"code": code, "message": message}}

def score(category, description, duration=""):
    text = (description + " " + duration).lower(); severity = 25
    if any(x in text for x in ("danger", "accident", "fire", "school", "hospital")): severity = 45
    elif any(x in text for x in ("health", "unsafe", "dark", "overflow")): severity = 35
    affected = 20 if any(x in text for x in ("many", "area", "residents", "street")) else 8
    duration_points = 20 if re.search(r"(?:[3-9]|[1-9][0-9]+)\s*(?:day|din|days)", text) else 8
    evidence = 10 if "photo" in text or "image" in text else 0
    total = min(100, severity + affected + duration_points + evidence)
    priority = "CRITICAL" if total >= 80 else "HIGH" if total >= 60 else "MEDIUM" if total >= 40 else "LOW"
    return total, priority, severity, f"Severity={severity}; affected-area signal={affected}; duration={duration_points}; evidence={evidence}."

def understand(title, description, category, location):
    text = f"{title} {description}".lower()
    cats = {"waste": "Waste Management", "garbage": "Waste Management", "kachra": "Waste Management", "streetlight": "Streetlights", "light": "Streetlights", "water": "Water Supply", "road": "Roads"}
    selected = next((v for k, v in cats.items() if k in text), category or "Other")
    m = re.search(r"(\d+)\s*(?:days?|din)", text); duration = f"{m.group(1)} days" if m else "unknown"
    ward = re.search(r"ward\s*([\w-]+)", f"{location} {description}", re.I)
    return {"category": selected, "severity": "HIGH" if any(x in text for x in ("danger", "unsafe", "health")) else "MEDIUM", "location": location or (f"Ward {ward.group(1)}" if ward else "Unspecified"), "duration": duration, "affectedArea": "Reported vicinity", "summary": f"{selected} issue reported", "confidence": 0.78 if selected != "Other" else 0.45}

def analyze(c, complaint):
    understanding = understand(complaint["title"], complaint["description"], complaint["category"], complaint["location"])
    s, priority, severity, reason = score(understanding["category"], complaint["description"], understanding["duration"])
    related = rows(c, "SELECT id, title, category, ward, latitude, longitude FROM complaints WHERE id != ? AND category = ? AND (ward = ? OR ward IS NULL) ORDER BY created_at DESC LIMIT 50", (complaint["id"], understanding["category"], complaint["ward"]))
    analysis = {"understanding": understanding, "priorityScore": s, "priority": priority, "priorityReason": reason, "confidence": understanding["confidence"], "summary": understanding["summary"], "recommendation": f"Human review recommended; inspect the {understanding['category'].lower()} service area.", "relatedCount": len(related), "evidenceNote": "Evidence received; advanced visual analysis unavailable in current demo configuration."}
    c.execute("INSERT INTO ai_analyses(id, complaint_id, category, severity, priority_score, confidence, summary, extracted_entities, risk_factors, recommendation, priority_reason, created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)", (uid("AI-"), complaint["id"], understanding["category"], severity, s, understanding["confidence"], understanding["summary"], json.dumps(understanding), json.dumps([]), analysis["recommendation"], reason, now()))
    c.execute("UPDATE complaints SET category=?, severity=?, priority=?, status='AI_ANALYZED', updated_at=? WHERE id=?", (understanding["category"], severity, priority, now(), complaint["id"]))
    if len(related) >= 2:
        ward = complaint["ward"] or "Unspecified"; cluster = one(c, "SELECT * FROM clusters WHERE category=? AND ward=? AND status='ACTIVE'", (understanding["category"], ward))
        if not cluster:
            cluster_id = uid("CL-"); c.execute("INSERT INTO clusters(id,name,category,ward,similarity_score,complaint_count,status,created_at) VALUES(?,?,?,?,?,?,?,?)", (cluster_id, f"{ward} {understanding['category']} Pattern", understanding["category"], ward, .82, 1, "ACTIVE", now()))
        else: cluster_id = cluster["id"]
        c.execute("UPDATE complaints SET cluster_id=? WHERE id=? OR (category=? AND ward=?)", (cluster_id, complaint["id"], understanding["category"], ward))
        count = c.execute("SELECT COUNT(*) FROM complaints WHERE cluster_id=?", (cluster_id,)).fetchone()[0]
        c.execute("UPDATE clusters SET complaint_count=? WHERE id=?", (count, cluster_id))
        if count >= 3 and not one(c, "SELECT id FROM systemic_issues WHERE cluster_id=?", (cluster_id,)):
            si = uid("SI-"); c.execute("INSERT INTO systemic_issues(id,title,description,category,ward,priority,confidence,complaint_count,department_id,recommended_action,status,cluster_id,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (si, f"{ward} {understanding['category']} Failure", "Multiple related complaints indicate a recurring service disruption.", understanding["category"], ward, priority, .82, count, None, analysis["recommendation"], "OPEN", cluster_id, now(), now()))
            c.execute("INSERT INTO notifications(id,user_id,type,title,message,read,created_at) VALUES(?,?,?,?,?,?,?)", (uid("N-"), None, "SYSTEMIC_ISSUE", "Systemic issue detected", f"Human review recommended for {ward} {understanding['category']}.", 0, now()))
    c.execute("INSERT INTO notifications(id,user_id,type,title,message,read,created_at) VALUES(?,?,?,?,?,?,?)", (uid("N-"), complaint["user_id"], "AI_ANALYSIS", "AI assessment completed", f"Your complaint received a {priority} priority assessment.", 0, now()))
    return analysis

def validate(payload, partial=False):
    if not isinstance(payload, dict): return "Request body must be a JSON object"
    if not partial and (not str(payload.get("title", "")).strip() or not str(payload.get("description", "")).strip()): return "title and description are required"
    if "title" in payload and not 3 <= len(str(payload["title"])) <= 200: return "title must be 3-200 characters"
    if "description" in payload and not 10 <= len(str(payload["description"])) <= 10000: return "description must be 10-10000 characters"
    if "status" in payload and payload["status"] not in STATUSES: return "invalid status"
    for k in ("latitude", "longitude"):
        if k in payload and payload[k] is not None:
            try:
                if not (-90 <= float(payload[k]) <= 90 if k == "latitude" else -180 <= float(payload[k]) <= 180): return f"invalid {k}"
            except (TypeError, ValueError): return f"invalid {k}"
    return None

def token(user_id, role):
    value = f"{user_id}.{role}"; sig = hmac.new(SECRET.encode(), value.encode(), hashlib.sha256).hexdigest(); return value + "." + sig
def auth(handler):
    raw = handler.headers.get("Authorization", "")
    if not raw.startswith("Bearer "): return None
    try:
        value, sig = raw[7:].rsplit(".", 1)
        if not hmac.compare_digest(sig, hmac.new(SECRET.encode(), value.encode(), hashlib.sha256).hexdigest()): return None
        user, role = value.split("."); return {"id": user, "role": role}
    except ValueError: return None

class Handler(BaseHTTPRequestHandler):
    def send(self, status, body):
        self.send_response(status); self.send_header("Content-Type", "application/json"); self.send_header("Access-Control-Allow-Origin", os.getenv("FRONTEND_URL", "*")); self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization"); self.end_headers(); self.wfile.write(json.dumps(body).encode())
    def body(self):
        try: return json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        except json.JSONDecodeError: return None
    def do_OPTIONS(self): self.send(204, {})
    def do_GET(self): self.route("GET")
    def do_POST(self): self.route("POST")
    def do_PATCH(self): self.route("PATCH")
    def do_DELETE(self): self.route("DELETE")
    def route(self, method):
        path = urlparse(self.path).path; parts = [x for x in path.split("/") if x]; q = parse_qs(urlparse(self.path).query); c = conn()
        try:
            if path == "/health": return self.send(*ok({"database": "connected"}, "Healthy"))
            if path == "/api/auth/demo" and method == "POST":
                p=self.body() or {}; role=p.get("role", "CITIZEN"); role=role if role in ("CITIZEN","AUTHORITY","ADMIN") else "CITIZEN"; user=one(c,"SELECT * FROM users WHERE email=?",(p.get("email","demo@example.local"),))
                if not user: user={"id":uid("U-"),"name":p.get("name","Demo User"),"email":p.get("email","demo@example.local"),"role":role}; c.execute("INSERT INTO users(id,name,email,role,created_at,updated_at) VALUES(?,?,?,?,?,?)",(user["id"],user["name"],user["email"],user["role"],now(),now()))
                return self.send(*ok({"user":user,"token":token(user["id"],user["role"])}))
            if path == "/api/complaints" and method == "POST":
                p=self.body(); e=validate(p); 
                if e:return self.send(*err("VALIDATION_ERROR",e))
                user=auth(self); user_id=user["id"] if user else p.get("userId")
                if not user_id:
                    user_id=uid("U-"); c.execute("INSERT INTO users(id,name,email,role,created_at,updated_at) VALUES(?,?,?,?,?,?)",(user_id,"Anonymous Demo Citizen",f"{user_id}@local.demo","CITIZEN",now(),now()))
                elif not one(c,"SELECT id FROM users WHERE id=?",(user_id,)): return self.send(*err("UNAUTHORIZED","Unknown user",401))
                cid=uid("C-"); c.execute("INSERT INTO complaints(id,user_id,title,description,category,location,latitude,longitude,ward,priority,severity,status,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(cid,user_id,p["title"].strip(),p["description"].strip(),p.get("category","Other"),p.get("location"),p.get("latitude"),p.get("longitude"),p.get("ward"),"LOW","LOW","SUBMITTED",now(),now())); c.commit(); return self.send(*ok(one(c,"SELECT * FROM complaints WHERE id=?",(cid,)),"Complaint created",201))
            if parts[:2] == ["api","complaints"] and len(parts)>=3:
                cid=parts[2]; complaint=one(c,"SELECT * FROM complaints WHERE id=?",(cid,))
                if not complaint:return self.send(*err("NOT_FOUND","Complaint not found",404))
                if len(parts)==4 and parts[3]=="analyze" and method=="POST":
                    if one(c,"SELECT id FROM ai_analyses WHERE complaint_id=? ORDER BY created_at DESC LIMIT 1",(cid,)): return self.send(*ok(one(c,"SELECT * FROM ai_analyses WHERE complaint_id=? ORDER BY created_at DESC LIMIT 1",(cid,)),"Existing AI assessment returned"))
                    c.execute("UPDATE complaints SET status='AI_ANALYZING',updated_at=? WHERE id=?",(now(),cid)); result=analyze(c,complaint); c.commit(); return self.send(*ok(result,"AI assessment completed"))
                if len(parts)==4 and parts[3]=="related" and method=="GET": return self.send(*ok(rows(c,"SELECT * FROM complaints WHERE category=? AND ward=? AND id!=? ORDER BY created_at DESC LIMIT 50",(complaint["category"],complaint["ward"],cid))))
                if method=="PATCH":
                    p=self.body() or {}; e=validate(p,True)
                    if e:return self.send(*err("VALIDATION_ERROR",e))
                    if "status" in p and p["status"] not in TRANSITIONS.get(complaint["status"],set()): return self.send(*err("INVALID_TRANSITION",f"Cannot transition {complaint['status']} to {p['status']}",409))
                    fields=[k for k in p if k in ("title","description","category","location","latitude","longitude","ward","priority","status","assigned_department_id")]; c.execute(f"UPDATE complaints SET {','.join(x+'=?' for x in fields)},updated_at=? WHERE id=?",[p[x] for x in fields]+[now(),cid]); c.commit(); return self.send(*ok(one(c,"SELECT * FROM complaints WHERE id=?",(cid,)),"Complaint updated"))
                if method=="DELETE": c.execute("DELETE FROM complaints WHERE id=?",(cid,)); c.commit(); return self.send(*ok(None,"Complaint deleted"))
                return self.send(*ok(complaint))
            if path == "/api/complaints" and method == "GET":
                page=max(1,int(q.get("page",[1])[0])); limit=min(100,max(1,int(q.get("limit",[20])[0]))); where=[]; args=[]
                for key in ("category","priority","status","ward"):
                    if key in q: where.append(key+"=?"); args.append(q[key][0])
                if "search" in q: where.append("(id LIKE ? OR title LIKE ? OR description LIKE ? OR location LIKE ?)"); args += [f"%{q['search'][0]}%"]*4
                clause=" WHERE "+" AND ".join(where) if where else ""; total=c.execute("SELECT COUNT(*) FROM complaints"+clause,args).fetchone()[0]; data=rows(c,"SELECT * FROM complaints"+clause+" ORDER BY created_at DESC LIMIT ? OFFSET ?",args+[limit,(page-1)*limit]); return self.send(*ok({"data":data,"page":page,"limit":limit,"total":total,"totalPages":(total+limit-1)//limit}))
            if path in ("/api/departments","/api/systemic-issues","/api/notifications") and method=="GET":
                table={"/api/departments":"departments","/api/systemic-issues":"systemic_issues","/api/notifications":"notifications"}[path]; return self.send(*ok(rows(c,"SELECT * FROM "+table+" ORDER BY created_at DESC LIMIT 100")))
            if path == "/api/analytics" and method=="GET": return self.send(*ok({"totalComplaints":c.execute("SELECT COUNT(*) FROM complaints").fetchone()[0],"activeComplaints":c.execute("SELECT COUNT(*) FROM complaints WHERE status NOT IN ('RESOLVED','REJECTED')").fetchone()[0],"criticalComplaints":c.execute("SELECT COUNT(*) FROM complaints WHERE priority='CRITICAL'").fetchone()[0],"systemicIssues":c.execute("SELECT COUNT(*) FROM systemic_issues").fetchone()[0],"resolutionRate":c.execute("SELECT COALESCE(AVG(status='RESOLVED')*100,0) FROM complaints").fetchone()[0]}))
            if path.startswith("/api/map-data") and method=="GET": return self.send(*ok(rows(c,"SELECT id,latitude,longitude,priority,category,cluster_id AS clusterId,ward FROM complaints WHERE latitude IS NOT NULL AND longitude IS NOT NULL LIMIT 500")))
            return self.send(*err("NOT_FOUND","Endpoint not found",404))
        except sqlite3.IntegrityError as ex: c.rollback(); log.warning("constraint failure: %s",ex); self.send(*err("CONFLICT","Request conflicts with existing data",409))
        except Exception: c.rollback(); log.exception("request failed"); self.send(*err("INTERNAL_ERROR","An internal error occurred",500))
        finally: c.close()

def main():
    init_db(); port=int(os.getenv("PORT","3000")); log.info("JAN-SHIELD API listening on %s",port); ThreadingHTTPServer((os.getenv("HOST","0.0.0.0"),port),Handler).serve_forever()
if __name__ == "__main__": main()
