import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routes import auth, email, whatsapp, rules, dashboard, admin, billing

_worker_task = None

async def _start_worker():
    from app.workers.email_poller import start_worker_loop
    await start_worker_loop(interval_seconds=300)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _worker_task
    init_db()
    _worker_task = asyncio.create_task(_start_worker())
    yield
    if _worker_task:
        _worker_task.cancel()

app = FastAPI(title="MailPilot", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(email.router)
app.include_router(whatsapp.router)
app.include_router(rules.router)
app.include_router(dashboard.router)
app.include_router(admin.router)
app.include_router(billing.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "mailpilot"}


@app.post("/api/worker/poll")
async def manual_poll():
    from app.workers.email_poller import poll_all_tenants
    await poll_all_tenants()
    return {"status": "ok", "message": "Poll completed"}
