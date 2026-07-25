"""
Standard CRUD for complaints, plus the "Commit to QMS Ledger" action which is
the button shown at the bottom of the AI risk assessment panel in the demo —
it's the moment a draft (AI-assisted) complaint becomes an official QMS record.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.core.database import get_db
from app.models.complaint import Complaint, ComplaintStatus, AuditLog
from app.schemas.complaint import ComplaintCreate, ComplaintUpdate, ComplaintOut, DashboardStats

router = APIRouter(prefix="/api/complaints", tags=["complaints"])


@router.get("", response_model=list[ComplaintOut])
def list_complaints(db: Session = Depends(get_db)):
    stmt = select(Complaint).order_by(Complaint.created_at.desc())
    return db.execute(stmt).scalars().all()


@router.get("/{complaint_id}", response_model=ComplaintOut)
def get_complaint(complaint_id: str, db: Session = Depends(get_db)):
    complaint = db.get(Complaint, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint


@router.post("", response_model=ComplaintOut)
def commit_complaint(payload: ComplaintCreate, db: Session = Depends(get_db)):
    """'Commit to QMS Ledger' — creates the permanent record from the AI-assisted draft."""
    complaint = Complaint(status=ComplaintStatus.READY_TO_COMMIT, **payload.model_dump())
    db.add(complaint)
    db.commit()
    db.refresh(complaint)

    db.add(AuditLog(
        complaint_id=complaint.id,
        action="COMMITTED_TO_LEDGER",
        actor="qa_user",
        details=f"Complaint {complaint.complaint_number} committed with AI-suggested severity "
                f"{complaint.ai_severity_suggested}.",
    ))
    complaint.status = ComplaintStatus.COMMITTED
    from datetime import datetime
    complaint.committed_at = datetime.utcnow()
    db.commit()
    db.refresh(complaint)
    return complaint


@router.put("/{complaint_id}", response_model=ComplaintOut)
def update_complaint(complaint_id: str, payload: ComplaintUpdate, db: Session = Depends(get_db)):
    complaint = db.get(Complaint, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    updates = payload.model_dump(exclude_unset=True)
    for k, v in updates.items():
        setattr(complaint, k, v)
    db.add(AuditLog(complaint_id=complaint.id, action="FIELD_UPDATED", details=str(updates)))
    db.commit()
    db.refresh(complaint)
    return complaint


@router.get("/stats/dashboard", response_model=DashboardStats)
def dashboard_stats(db: Session = Depends(get_db)):
    total = db.execute(select(func.count()).select_from(Complaint)).scalar_one()
    pending = db.execute(
        select(func.count()).select_from(Complaint).where(Complaint.status == ComplaintStatus.PENDING_TRIAGE)
    ).scalar_one()
    ready = db.execute(
        select(func.count()).select_from(Complaint).where(Complaint.status == ComplaintStatus.READY_TO_COMMIT)
    ).scalar_one()
    committed = db.execute(
        select(func.count()).select_from(Complaint).where(Complaint.status == ComplaintStatus.COMMITTED)
    ).scalar_one()
    critical = db.execute(
        select(func.count()).select_from(Complaint).where(Complaint.ai_severity_suggested == "Critical")
    ).scalar_one()
    major = db.execute(
        select(func.count()).select_from(Complaint).where(Complaint.ai_severity_suggested == "Major")
    ).scalar_one()
    minor = db.execute(
        select(func.count()).select_from(Complaint).where(Complaint.ai_severity_suggested == "Minor")
    ).scalar_one()

    return DashboardStats(
        total=total, pending_triage=pending, ready_to_commit=ready, committed=committed,
        critical=critical, major=major, minor=minor,
    )
