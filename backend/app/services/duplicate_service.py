"""
Fetches a lightweight list of recent complaints for the duplicate-detection
node to compare against. Kept simple: last 25 complaints, only the fields
that matter for similarity (product, batch, category, description).
"""
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.complaint import Complaint


def get_recent_complaints_for_comparison(db: Session, exclude_id: str | None = None, limit: int = 25) -> list[dict]:
    stmt = select(Complaint).order_by(Complaint.created_at.desc()).limit(limit)
    rows = db.execute(stmt).scalars().all()
    out = []
    for c in rows:
        if exclude_id and c.id == exclude_id:
            continue
        out.append({
            "id": c.id,
            "complaint_number": c.complaint_number,
            "product_name": c.product_name,
            "batch_lot_number": c.batch_lot_number,
            "complaint_category": c.complaint_category,
            "complaint_description": c.complaint_description,
        })
    return out
