"""
Each function here is one LangGraph node: it takes the current AgentState,
does one focused job (usually one Groq call), and returns a dict of state
updates. Keeping nodes small is what makes the graph easy to reason about,
extend (e.g. add a new bonus-feature node), and demo/explain.
"""
import json
import logging

from app.agent.state import AgentState
from app.agent import prompts
from app.services.groq_client import chat_completion_json, chat_completion

logger = logging.getLogger("aivoa.agent")


def _trace(state: AgentState, node_name: str) -> list[str]:
    return state.get("trace", []) + [node_name]


# ---------------------------------------------------------------------------
# 1. Intent routing
# ---------------------------------------------------------------------------
def classify_intent(state: AgentState) -> dict:
    # If a document/PDF was attached, we always treat this as a new complaint —
    # matches the demo: dropping a PDF always triggers full extraction.
    if state.get("attachment_text"):
        return {"intent": "new_complaint", "trace": _trace(state, "classify_intent(attachment→new_complaint)")}

    result = chat_completion_json(
        prompts.INTENT_CLASSIFIER_SYSTEM,
        f"Message: {state['user_message']}\n\nDoes a draft complaint already have fields filled? {bool(state.get('existing_fields'))}",
    )
    intent = result.get("intent", "new_complaint")
    return {"intent": intent, "trace": _trace(state, f"classify_intent({intent})")}


def route_by_intent(state: AgentState) -> str:
    return state.get("intent", "new_complaint")


# ---------------------------------------------------------------------------
# 2a. New-complaint pipeline
# ---------------------------------------------------------------------------
def extract_fields(state: AgentState) -> dict:
    source_text = state.get("attachment_text") or state["user_message"]
    result = chat_completion_json(prompts.EXTRACTION_SYSTEM, source_text)
    # Merge onto any existing fields rather than overwriting known data with nulls
    merged = {**state.get("existing_fields", {})}
    for k, v in result.items():
        if v not in (None, "", "null"):
            merged[k] = v
    return {"fields": merged, "trace": _trace(state, "extract_fields")}


def check_completeness(state: AgentState) -> dict:
    result = chat_completion_json(prompts.COMPLETENESS_SYSTEM, json.dumps(state["fields"]))
    assessment = {**state.get("assessment", {}), "ai_completeness_notes": result.get("notes", "")}
    return {"assessment": assessment, "trace": _trace(state, "check_completeness")}


def classify_risk(state: AgentState) -> dict:
    result = chat_completion_json(prompts.RISK_CLASSIFIER_SYSTEM, json.dumps(state["fields"]))
    assessment = {
        **state.get("assessment", {}),
        "ai_severity_suggested": result.get("severity"),
        "ai_suggested_next_action": result.get("suggested_next_action"),
        "ai_initial_risk_assessment": result.get("initial_risk_assessment"),
    }
    return {"assessment": assessment, "trace": _trace(state, "classify_risk")}


def detect_duplicates(state: AgentState) -> dict:
    existing = state.get("existing_complaints", [])
    if not existing:
        return {"duplicates": [], "trace": _trace(state, "detect_duplicates(none-to-compare)")}
    payload = json.dumps({"new_complaint": state["fields"], "existing_complaints": existing})
    result = chat_completion_json(prompts.DUPLICATE_SYSTEM, payload)
    matches = result.get("matches", [])
    return {"duplicates": matches, "trace": _trace(state, f"detect_duplicates({len(matches)} found)")}


def suggest_root_cause(state: AgentState) -> dict:
    result = chat_completion_json(prompts.ROOT_CAUSE_SYSTEM, json.dumps(state["fields"]))
    assessment = {**state.get("assessment", {}), "ai_root_cause_suggestion": result.get("root_cause_suggestion")}
    return {"assessment": assessment, "trace": _trace(state, "suggest_root_cause")}


def suggest_capa(state: AgentState) -> dict:
    payload = json.dumps({
        "fields": state["fields"],
        "root_cause": state.get("assessment", {}).get("ai_root_cause_suggestion"),
    })
    result = chat_completion_json(prompts.CAPA_SYSTEM, payload)
    assessment = {**state.get("assessment", {}), "ai_capa_suggestion": result.get("capa_suggestion")}
    return {"assessment": assessment, "trace": _trace(state, "suggest_capa")}


def summarize(state: AgentState) -> dict:
    payload = json.dumps({"fields": state["fields"], "assessment": state.get("assessment", {})})
    result = chat_completion_json(prompts.SUMMARY_SYSTEM, payload)
    assessment = {**state.get("assessment", {}), "ai_summary": result.get("ai_summary")}
    return {"assessment": assessment, "trace": _trace(state, "summarize")}


def compose_new_complaint_reply(state: AgentState) -> dict:
    fields = state["fields"]
    source = "PDF/document" if state.get("attachment_text") else "message"
    reply = (
        f"Complaint parsed successfully from the {source}. I've extracted the product details, "
        f"mapped the batch information, and generated an initial risk assessment"
        + (f" ({state['assessment'].get('ai_severity_suggested')})." if state.get("assessment", {}).get("ai_severity_suggested") else ".")
    )
    if state.get("assessment", {}).get("ai_completeness_notes"):
        reply += f" Note: {state['assessment']['ai_completeness_notes']}"
    if state.get("duplicates"):
        reply += f" I also found {len(state['duplicates'])} potentially similar past complaint(s) — please review."
    return {"reply": reply, "trace": _trace(state, "compose_new_complaint_reply")}


# ---------------------------------------------------------------------------
# 2b. Correction pipeline (lightweight — just updates one or two fields)
# ---------------------------------------------------------------------------
def apply_correction(state: AgentState) -> dict:
    payload = json.dumps({"current_fields": state.get("existing_fields", {}), "user_message": state["user_message"]})
    result = chat_completion_json(prompts.CORRECTION_SYSTEM, payload)
    merged = {**state.get("existing_fields", {}), **{k: v for k, v in result.items() if v}}

    changed = ", ".join(f'"{k}" to "{v}"' for k, v in result.items() if v) or "the requested field"
    reply = f"Got it. I have updated {changed} in the form."
    return {"fields": merged, "reply": reply, "trace": _trace(state, "apply_correction")}


# ---------------------------------------------------------------------------
# 2c. Chit-chat pipeline
# ---------------------------------------------------------------------------
def chit_chat(state: AgentState) -> dict:
    reply = chat_completion(prompts.CHITCHAT_SYSTEM, state["user_message"], json_mode=False)
    return {
        "fields": state.get("existing_fields", {}),
        "reply": reply,
        "trace": _trace(state, "chit_chat"),
    }
