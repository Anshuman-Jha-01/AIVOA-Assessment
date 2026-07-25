"""
The AgentState is the single object that flows through every node of the
LangGraph graph. Each node reads what it needs from it and returns a dict
of the keys it wants to update — LangGraph merges that into the state.
"""
from typing import TypedDict, Literal


class AgentState(TypedDict, total=False):
    # --- input ---
    session_id: str
    user_message: str
    attachment_text: str | None   # raw text pulled from an uploaded PDF/email, if any
    existing_fields: dict         # fields already known for this draft complaint (from prior turns)
    existing_complaints: list[dict]  # lightweight list of other complaints, for duplicate detection

    # --- routing ---
    intent: Literal["new_complaint", "correction", "chit_chat"]

    # --- working data / outputs ---
    fields: dict            # ComplaintFields, merged
    assessment: dict        # AIAssessment (severity, next action, risk text, root cause, CAPA, summary)
    duplicates: list[dict]  # potential duplicate complaints found
    reply: str              # final chat message shown to the QA user

    trace: list[str]        # names of nodes visited, for demo/debugging transparency
