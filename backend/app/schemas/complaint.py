"""
Pydantic schemas = the "contract" between frontend and backend.

- `ComplaintFields` is reused in THREE places, which is the key design idea:
    1. The shape the LLM must return (structured extraction output)
    2. The shape the frontend form edits
    3. The shape stored partially/fully in the DB
  Keeping one shared field set means the AI agent, the API, and the React
  form are always talking about the same fields.
"""
from datetime import datetime
from pydantic import BaseModel, Field


class ComplaintFields(BaseModel):
    """All the editable business fields of a complaint. Every field is optional
    because the AI fills them in incrementally as it extracts information."""
    complaint_source: str | None = None
    customer_name: str | None = None

    product_name: str | None = None
    product_strength: str | None = None
    batch_lot_number: str | None = None
    affected_quantity: str | None = None
    manufacturing_date: str | None = None
    expiry_date: str | None = None

    originating_site_block: str | None = None
    impacted_npm: str | None = None

    complaint_category: str | None = None
    complaint_description: str | None = None


class AIAssessment(BaseModel):
    ai_severity_suggested: str | None = None
    ai_suggested_next_action: str | None = None
    ai_initial_risk_assessment: str | None = None
    ai_root_cause_suggestion: str | None = None
    ai_capa_suggestion: str | None = None
    ai_summary: str | None = None
    ai_completeness_notes: str | None = None


class ComplaintCreate(ComplaintFields, AIAssessment):
    """Used when committing a complaint to the QMS ledger."""
    pass


class ComplaintUpdate(ComplaintFields, AIAssessment):
    status: str | None = None


class ComplaintOut(ComplaintFields, AIAssessment):
    id: str
    complaint_number: str
    status: str
    created_at: datetime
    updated_at: datetime
    committed_at: datetime | None = None

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total: int
    pending_triage: int
    ready_to_commit: int
    committed: int
    critical: int
    major: int
    minor: int
