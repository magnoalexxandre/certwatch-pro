import os
from typing import List
from fastapi import FastAPI, HTTPException, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import bcrypt
from starlette.middleware.sessions import SessionMiddleware
import uvicorn
import notifier
import database

API_TOKEN     = os.getenv("API_TOKEN", "change-this-secure-token")
ALERT_DAYS    = [int(d) for d in os.getenv("ALERT_DAYS", "30,20,10,7,3,1").split(",")]
SECRET_KEY    = os.getenv("SECRET_KEY", "change-this-secret-key")
ADMIN_USER    = os.getenv("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "changeme")

_admin_hash: bytes = b""

app = FastAPI(title="CertMonitor")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY, max_age=86400)
templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
def startup():
    global _admin_hash
    database.init_db()
    _admin_hash = bcrypt.hashpw(ADMIN_PASSWORD.encode(), bcrypt.gensalt())


# --- Modelos ---

class Certificate(BaseModel):
    hostname: str
    path: str
    subject: str
    issuer: str
    not_before: str
    not_after: str
    days_remaining: int
    serial_number: str
    fingerprint: str
    cert_type: str

class CertificateReport(BaseModel):
    hostname: str
    certificates: List[Certificate]
    timestamp: str


# --- Helpers ---

def _verify_agent_token(request: Request):
    token = request.headers.get("X-API-Token")
    if token != API_TOKEN:
        raise HTTPException(status_code=401, detail="Token inválido")

def _require_login(request: Request):
    if not request.session.get("authenticated"):
        return False
    return True

def _status_color(days: int) -> str:
    if days < 0:        return "expired"
    elif days <= 10:    return "critical"
    elif days <= 20:    return "warning"
    return "ok"


# --- Auth ---

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if request.session.get("authenticated"):
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_USER and bcrypt.checkpw(password.encode(), _admin_hash):
        request.session["authenticated"] = True
        request.session["username"] = username
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Usuário ou senha inválidos"})

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)


# --- API (agentes) ---

@app.post("/api/report")
async def receive_report(report: CertificateReport, request: Request):
    _verify_agent_token(request)
    certs_dicts = [c.dict() for c in report.certificates]
    database.upsert_report(report.hostname, certs_dicts, report.timestamp)
    notifier.check_and_notify(database.get_all_certificates())
    return {"status": "success", "certificates_received": len(report.certificates)}

@app.get("/health")
async def health():
    return {"status": "healthy"}


# --- Dashboard ---

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    if not _require_login(request):
        return RedirectResponse(url="/login", status_code=302)

    certs = database.get_all_certificates()
    for cert in certs:
        cert["status_color"] = _status_color(cert["days_remaining"])

    return templates.TemplateResponse("index.html", {
        "request":      request,
        "certificates": certs,
        "stats":        database.get_stats(),
        "agent_status": database.get_agent_status(),
        "username":     request.session.get("username"),
        "alert_days":   ALERT_DAYS,
    })


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
