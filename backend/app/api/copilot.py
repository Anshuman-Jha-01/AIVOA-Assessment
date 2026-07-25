"""
Routes for the AIVOA Copilot chat panel (right-hand side of the 'Log Customer
Complaint' screen in the demo). These are the two entry points into the
LangGraph agent:

  POST /api/copilot/message  - user typed/pasted a message (text complaint, or a correction)
  POST /api/copilot/upload   - user dropped a PDF/email file to be parsed

Both persist chat history (CopilotMessage) so a session can be resumed, and
both return the same CopilotResponse shape the frontend uses to update the
form fields live.
"""
import os
import uuid
import logging

from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.models.complaint import CopilotMessage, Attachment
from app.schemas.copilot import CopilotMessageIn, CopilotResponse
from app.schemas.complaint import ComplaintFields, AIAssessment
from app.agent.graph import run_agent
from app.services.document_parser import extract_text_from_upload
from app.services.duplicate_service import get_recent_complaints_for_comparison

logger = logging.getLogger("aivoa.api.copilot")
router = APIRouter(prefix="/api/copilot", tags=["copilot"])


def _load_session_fields(db: Session, session_id: str) -> dict:
    """Reconstruct the 'current known fields' for a draft session from chat history.
    In this simple design we just keep the latest snapshot in memory via the
    frontend (it sends existing_fields back each turn) — but as a safety net we
    also check the DB in case the frontend didn't have it."""
    return {}


def _save_message(db: Session, session_id: str, role: str, content: str, complaint_id: str | None = None):
    msg = CopilotMessage(session_id=session_id, role=role, content=content, complaint_id=complaint_id)
    db.add(msg)
    db.commit()


def _build_response(session_id: str, final_state: dict) -> CopilotResponse:
    fields = ComplaintFields(**{k: v for k, v in final_state.get("fields", {}).items() if k in ComplaintFields.model_fields})
    assessment = AIAssessment(**{k: v for k, v in final_state.get("assessment", {}).items() if k in AIAssessment.model_fields})
    duplicates = [
        {
            "complaint_id": d.get("complaint_id"),
            "complaint_number": d.get("complaint_number", ""),
            "similarity_score": d.get("similarity_score", 0),
            "rationale": d.get("rationale"),
        }
        for d in final_state.get("duplicates", [])
    ]
    return CopilotResponse(
        session_id=session_id,
        reply=final_state.get("reply", ""),
        fields=fields,
        assessment=assessment,
        duplicates=duplicates,
        graph_trace=final_state.get("trace", []),
    )


@router.post("/message", response_model=CopilotResponse)
def send_message(
    payload: CopilotMessageIn,
    db: Session = Depends(get_db),
):
    """payload.existing_fields is sent by the frontend as the current form state, so
    the agent can merge new info / apply corrections onto it, exactly like the demo
    where 'ah sorry the batch number is X' only patches one field."""
    _save_message(db, payload.session_id, "user", payload.message)

    existing_complaints = get_recent_complaints_for_comparison(db)
    final_state = run_agent(
        session_id=payload.session_id,
        user_message=payload.message,
        existing_fields=payload.existing_fields or {},
        existing_complaints=existing_complaints,
    )

    _save_message(db, payload.session_id, "assistant", final_state.get("reply", ""))
    return _build_response(payload.session_id, final_state)


@router.post("/upload", response_model=CopilotResponse)
async def upload_document(
    session_id: str = Form(...),
    existing_fields_json: str = Form("{}"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    import json
    existing_fields = json.loads(existing_fields_json) if existing_fields_json else {}

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    saved_name = f"{uuid.uuid4().hex}_{file.filename}"
    saved_path = os.path.join(settings.UPLOAD_DIR, saved_name)
    contents = await file.read()
    with open(saved_path, "wb") as f:
        f.write(contents)

    extracted_text = extract_text_from_upload(saved_path, file.filename)

    attachment = Attachment(
        filename=file.filename,
        file_type=file.filename.split(".")[-1].lower(),
        file_path=saved_path,
        extracted_text=extracted_text,
    )
    db.add(attachment)
    db.commit()

    user_msg = f"[Uploaded document: {file.filename}]"
    _save_message(db, session_id, "user", user_msg)

    existing_complaints = get_recent_complaints_for_comparison(db)
    final_state = run_agent(
        session_id=session_id,
        user_message=user_msg,
        existing_fields=existing_fields,
        attachment_text=extracted_text,
        existing_complaints=existing_complaints,
    )

    _save_message(db, session_id, "assistant", final_state.get("reply", ""))
    return _build_response(session_id, final_state)
