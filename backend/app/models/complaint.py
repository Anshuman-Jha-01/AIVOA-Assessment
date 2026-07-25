"""
The Complaint table mirrors the 4 sections of the 'Log Customer Complaint'
form shown in the demo:
  1. Origin & Customer Details
  2. Product & Batch Identification
  3. Facility & Material Impact
  4. Defect Analysis (+ AI Copilot risk assessment fields)

Plus AI-generated bonus fields: root cause, CAPA suggestion, and summary.
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ComplaintStatus(str, enum.Enum):
    PENDING_TRIAGE = "PENDING_TRIAGE"   # AI has not finished processing yet
    READY_TO_COMMIT = "READY_TO_COMMIT" # AI processed, waiting for QA to commit
    COMMITTED = "COMMITTED"             # Saved to the QMS ledger (final)
    CLOSED = "CLOSED"


class Severity(str, enum.Enum):
    CRITICAL = "Critical"
    MAJOR = "Major"
    MINOR = "Minor"


def gen_complaint_number() -> str:
    return f"CC-{datetime.utcnow().year}-{uuid.uuid4().hex[:6].upper()}"


class Complaint(Base):
    __tablename__ = "complaints"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    complaint_number: Mapped[str] = mapped_column(String(50), unique=True, default=gen_complaint_number)

    status: Mapped[ComplaintStatus] = mapped_column(
        Enum(ComplaintStatus), default=ComplaintStatus.PENDING_TRIAGE
    )

    # 1. Origin & Customer Details
    complaint_source: Mapped[str | None] = mapped_column(String(100), nullable=True)   # e.g. Pharmacy, Email, Distributor
    customer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # 2. Product & Batch Identification
    product_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    product_strength: Mapped[str | None] = mapped_column(String(100), nullable=True)
    batch_lot_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    affected_quantity: Mapped[str | None] = mapped_column(String(100), nullable=True)
    manufacturing_date: Mapped[str | None] = mapped_column(String(50), nullable=True)
    expiry_date: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # 3. Facility & Material Impact
    originating_site_block: Mapped[str | None] = mapped_column(String(100), nullable=True)  # e.g. Manufacturing, Packaging
    impacted_npm: Mapped[str | None] = mapped_column(String(255), nullable=True)  # Non-Product Materials, e.g. Primary Packaging

    # 4. Defect Analysis
    complaint_category: Mapped[str | None] = mapped_column(String(255), nullable=True)
    complaint_description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # AI Copilot risk assessment
    ai_severity_suggested: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ai_suggested_next_action: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ai_initial_risk_assessment: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Bonus AI features
    ai_root_cause_suggestion: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_capa_suggestion: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_completeness_notes: Mapped[str | None] = mapped_column(Text, nullable=True)  # missing-field warnings

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    committed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    attachments: Mapped[list["Attachment"]] = relationship(back_populates="complaint", cascade="all, delete-orphan")
    messages: Mapped[list["CopilotMessage"]] = relationship(back_populates="complaint", cascade="all, delete-orphan")


class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    complaint_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("complaints.id"), nullable=True)
    filename: Mapped[str] = mapped_column(String(255))
    file_type: Mapped[str] = mapped_column(String(50))  # "pdf" | "image" | "text"
    file_path: Mapped[str] = mapped_column(String(500))
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    complaint: Mapped["Complaint"] = relationship(back_populates="attachments")


class CopilotMessage(Base):
    """Chat history for the AIVOA Copilot panel, scoped to a draft session or a committed complaint."""
    __tablename__ = "copilot_messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(String(36), index=True)  # groups messages before a complaint is committed
    complaint_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("complaints.id"), nullable=True)
    role: Mapped[str] = mapped_column(String(20))  # "user" | "assistant"
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    complaint: Mapped["Complaint"] = relationship(back_populates="messages")


class DuplicateMatch(Base):
    """Stores AI-detected potential duplicate complaints for review."""
    __tablename__ = "duplicate_matches"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    complaint_id: Mapped[str] = mapped_column(String(36), ForeignKey("complaints.id"))
    matched_complaint_id: Mapped[str] = mapped_column(String(36), ForeignKey("complaints.id"))
    similarity_score: Mapped[float] = mapped_column()
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    """Append-only trail — required in any real QMS module for traceability (21 CFR Part 11 style)."""
    __tablename__ = "audit_log"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    complaint_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("complaints.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(100))  # e.g. "COMMITTED_TO_LEDGER", "FIELD_UPDATED"
    actor: Mapped[str] = mapped_column(String(100), default="system")
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
