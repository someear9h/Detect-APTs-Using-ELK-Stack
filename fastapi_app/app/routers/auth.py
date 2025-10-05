from fastapi import APIRouter, Request
from datetime import datetime
import uuid
from ..models.schemas import LoginIn, ExecIn
from ..utils.logshipper import send_to_logstash
from ..config import settings


router = APIRouter()


@router.get("/health")
async def health():
    return {"ok": True}


@router.post("/login")
async def login(payload: LoginIn, request: Request):
    correct_password = "password"  # last password in brute-force list
    success = payload.password == correct_password

    event = {
        "@timestamp": datetime.utcnow().isoformat() + "Z",
        "event_id": str(uuid.uuid4()),
        "app": settings.APP_NAME,
        "path": "/login",
        "action": "login",
        "user": payload.username,
        "status": 200 if success else 401,
        "client_ip": request.client.host,
        "message": f"Login {'success' if success else 'failed'} for {payload.username}",
        "bytes_out": 0
    }
    send_to_logstash(event)
    return {"ok": success}



@router.post("/exec")
async def exec_cmd(payload: ExecIn, request: Request):
    # Simulated process execution log (powershell etc.)
    event = {
        "@timestamp": datetime.utcnow().isoformat() + "Z",
        "event_id": str(uuid.uuid4()),
        "app": settings.APP_NAME,
        "path": "/exec",
        "action": "process_exec",
        "user": payload.user or "unknown",
        "status": 200,
        "client_ip": payload.client_ip or request.client.host,
        "message": f"Executed: {payload.command_line}",
        "command_line": payload.command_line,
        "bytes_out": payload.bytes_out or 0
    }
    send_to_logstash(event)
    return {"ok": True}