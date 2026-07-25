from pydantic import BaseModel
from app.schemas.complaint import ComplaintFields, AIAssessment


class CopilotMessageIn(BaseModel):
    session_id: str
    message: str
    existing_fields: dict = {}


class DuplicateMatchOut(BaseModel):
    complaint_id: str
    complaint_number: str
    similarity_score: float
    rationale: str | None = None


class CopilotResponse(BaseModel):
    """
    Everything the frontend needs after one turn of the AI agent:
    - the assistant's chat reply text
    - the (possibly partial) structured fields to merge into the form
    - the AI risk assessment block
    - duplicate warnings, if any
    - which node the graph ended on (useful for debugging / demo narration)
    """
    session_id: str
    reply: str
    fields: ComplaintFields
    assessment: AIAssessment
    duplicates: list[DuplicateMatchOut] = []
    graph_trace: list[str] = []
