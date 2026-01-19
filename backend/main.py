"""
Admin API Backend for BookReading Website
==========================================
FastAPI server to run Python scripts from web interface.
Now with JWT authentication for single admin user.

Endpoints:
    POST /api/login      - Login and get token
    POST /api/scrape     - Run chapter scraper
    POST /api/translate  - Run translation
    POST /api/format     - Format chapters for website
    POST /api/update     - Update chapters.json
    GET  /api/status     - Get current task status
    GET  /api/logs       - SSE stream for real-time logs

Run with:
    uvicorn main:app --reload --port 8000
"""

import asyncio
import sys
import os
import secrets
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
from contextlib import asynccontextmanager
import queue

from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel

# ============================================
# CONFIGURATION - Change these for production!
# ============================================
# Default admin credentials (change in production!)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "dat4512")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Dat4512@")
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(32))
TOKEN_EXPIRE_HOURS = 24

# Paths
BACKEND_DIR = Path(__file__).parent
PROJECT_DIR = BACKEND_DIR.parent
SCRIPTS_DIR = PROJECT_DIR / "scripts"

# Token storage (in-memory, simple approach)
active_tokens = {}

# Security
security = HTTPBearer(auto_error=False)


# ============================================
# Authentication Functions
# ============================================
def hash_password(password: str) -> str:
    """Hash password with SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()


def create_token() -> str:
    """Generate a secure random token."""
    return secrets.token_urlsafe(32)


def verify_token(token: str) -> bool:
    """Check if token is valid and not expired."""
    if token not in active_tokens:
        return False
    expires = active_tokens[token]
    if datetime.now() > expires:
        del active_tokens[token]
        return False
    return True


async def require_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to require authentication."""
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    token = credentials.credentials
    if not verify_token(token):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return token


# ============================================
# Task Manager
# ============================================
class TaskManager:
    def __init__(self):
        self.current_task: Optional[str] = None
        self.is_running: bool = False
        self.logs: list = []
        self.log_queue = queue.Queue()
        self.start_time: Optional[datetime] = None
        
    def start_task(self, name: str):
        self.current_task = name
        self.is_running = True
        self.logs = []
        self.start_time = datetime.now()
        self.add_log(f"🚀 Starting: {name}")
        
    def end_task(self, success: bool = True):
        duration = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        status = "✅ Completed" if success else "❌ Failed"
        self.add_log(f"{status} in {duration:.1f}s")
        self.is_running = False
        self.current_task = None
        
    def add_log(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        self.log_queue.put(log_entry)
        
    def get_status(self):
        return {
            "isRunning": self.is_running,
            "currentTask": self.current_task,
            "logCount": len(self.logs)
        }

task_manager = TaskManager()


# ============================================
# FastAPI App
# ============================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Backend server started")
    print(f"🔐 Admin user: {ADMIN_USERNAME}")
    yield
    print("👋 Backend server stopped")

app = FastAPI(
    title="BookReading Admin API",
    version="1.1.0",
    lifespan=lifespan
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# Request Models
# ============================================
class LoginRequest(BaseModel):
    username: str
    password: str

class ScrapeRequest(BaseModel):
    start_url: Optional[str] = None
    count: Optional[int] = 10

class TranslateRequest(BaseModel):
    force: bool = False

class FormatRequest(BaseModel):
    pass

class UpdateRequest(BaseModel):
    force: bool = False


# ============================================
# Helper Functions
# ============================================
async def run_script(script_name: str, args: list = None):
    """Run a Python script and stream output to logs."""
    script_path = SCRIPTS_DIR / script_name
    
    if not script_path.exists():
        task_manager.add_log(f"❌ Script not found: {script_name}")
        return False
    
    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)
    
    task_manager.add_log(f"📂 Running: {script_name}")
    
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=str(SCRIPTS_DIR)
        )
        
        while True:
            line = await process.stdout.readline()
            if not line:
                break
            decoded = line.decode('utf-8', errors='replace').rstrip()
            if decoded:
                task_manager.add_log(decoded)
        
        await process.wait()
        
        if process.returncode == 0:
            task_manager.add_log(f"✅ {script_name} completed successfully")
            return True
        else:
            task_manager.add_log(f"❌ {script_name} failed with code {process.returncode}")
            return False
            
    except Exception as e:
        task_manager.add_log(f"❌ Error running {script_name}: {str(e)}")
        return False


# ============================================
# Authentication Endpoints
# ============================================
@app.post("/api/login")
async def login(request: LoginRequest):
    """Authenticate and return token."""
    if request.username != ADMIN_USERNAME or request.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Create new token
    token = create_token()
    expires = datetime.now() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    active_tokens[token] = expires
    
    return {
        "token": token,
        "expires": expires.isoformat(),
        "message": "Login successful"
    }


@app.post("/api/logout")
async def logout(token: str = Depends(require_auth)):
    """Invalidate token."""
    if token in active_tokens:
        del active_tokens[token]
    return {"message": "Logged out successfully"}


@app.get("/api/verify")
async def verify(token: str = Depends(require_auth)):
    """Verify if token is still valid."""
    return {"valid": True, "message": "Token is valid"}


# ============================================
# Protected API Endpoints
# ============================================
@app.get("/api/status")
async def get_status(token: str = Depends(require_auth)):
    """Get current task status."""
    return task_manager.get_status()


@app.get("/api/logs")
async def get_logs(token: str = Depends(require_auth)):
    """Get all logs."""
    return {"logs": task_manager.logs}


@app.get("/api/logs/stream")
async def stream_logs(authorization: str = Header(None)):
    """SSE endpoint for real-time log streaming."""
    # Manual auth check for SSE (can't use Depends easily)
    if authorization:
        token = authorization.replace("Bearer ", "")
        if not verify_token(token):
            raise HTTPException(status_code=401, detail="Invalid token")
    else:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    async def event_generator():
        last_index = 0
        while True:
            current_logs = task_manager.logs
            if len(current_logs) > last_index:
                for log in current_logs[last_index:]:
                    yield {"event": "log", "data": log}
                last_index = len(current_logs)
            
            yield {"event": "status", "data": str(task_manager.is_running)}
            
            if not task_manager.is_running and last_index > 0:
                yield {"event": "done", "data": "Task completed"}
                break
                
            await asyncio.sleep(0.5)
    
    return EventSourceResponse(event_generator())


@app.post("/api/scrape")
async def run_scrape(request: ScrapeRequest, background_tasks: BackgroundTasks, token: str = Depends(require_auth)):
    """Run chapter scraper."""
    if task_manager.is_running:
        raise HTTPException(status_code=409, detail="Another task is already running")
    
    async def scrape_task():
        task_manager.start_task("Chapter Scraping")
        args = []
        if request.start_url:
            args.extend(["--url", request.start_url])
        if request.count:
            args.extend(["--count", str(request.count)])
        
        success = await run_script("auto_scrape.py", args if args else None)
        task_manager.end_task(success)
    
    background_tasks.add_task(scrape_task)
    return {"message": "Scraping started", "status": "running"}


@app.post("/api/translate")
async def run_translate(request: TranslateRequest, background_tasks: BackgroundTasks, token: str = Depends(require_auth)):
    """Run translation script."""
    if task_manager.is_running:
        raise HTTPException(status_code=409, detail="Another task is already running")
    
    async def translate_task():
        task_manager.start_task("Chapter Translation")
        args = ["--translate"] if not request.force else ["--translate", "--force"]
        success = await run_script("translate_chapters.py", args)
        task_manager.end_task(success)
    
    background_tasks.add_task(translate_task)
    return {"message": "Translation started", "status": "running"}


@app.post("/api/format")
async def run_format(background_tasks: BackgroundTasks, token: str = Depends(require_auth)):
    """Run format script."""
    if task_manager.is_running:
        raise HTTPException(status_code=409, detail="Another task is already running")
    
    async def format_task():
        task_manager.start_task("Format Chapters")
        success = await run_script("format_for_website.py")
        task_manager.end_task(success)
    
    background_tasks.add_task(format_task)
    return {"message": "Formatting started", "status": "running"}


@app.post("/api/update")
async def run_update(request: UpdateRequest, background_tasks: BackgroundTasks, token: str = Depends(require_auth)):
    """Run update chapters.json script."""
    if task_manager.is_running:
        raise HTTPException(status_code=409, detail="Another task is already running")
    
    async def update_task():
        task_manager.start_task("Update Website Data")
        args = ["--force"] if request.force else []
        success = await run_script("update_chapters_json.py", args if args else None)
        task_manager.end_task(success)
    
    background_tasks.add_task(update_task)
    return {"message": "Update started", "status": "running"}


@app.get("/api/chapters/status")
async def get_chapters_status(token: str = Depends(require_auth)):
    """Get status of chapters in each stage."""
    untranslated_dir = SCRIPTS_DIR / "Chapters_Untranslated"
    translated_dir = SCRIPTS_DIR / "Chapters_Translated"
    chapters_dir = PROJECT_DIR / "Chapters"
    
    def count_files(dir_path: Path) -> int:
        if dir_path.exists():
            return len(list(dir_path.glob("*.txt")))
        return 0
    
    return {
        "untranslated": count_files(untranslated_dir),
        "translated": count_files(translated_dir),
        "formatted": count_files(chapters_dir)
    }


# Health check (public)
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
