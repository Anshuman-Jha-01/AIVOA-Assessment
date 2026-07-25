import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base
from app.api import complaints, copilot

logging.basicConfig(level=logging.INFO)

# Create tables on startup if they don't exist yet.
# (For a real production system you'd use Alembic migrations instead — see README.)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AIVOA Customer Complaint Management API",
    description="AI-powered complaint intake, triage, and QMS ledger for pharmaceutical API/FDF manufacturers.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(complaints.router)
app.include_router(copilot.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "env": settings.APP_ENV}
