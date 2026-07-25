"""
This is where the graph topology is defined.

    START
      │
      ▼
 classify_intent ──"new_complaint"──▶ extract_fields ▶ check_completeness ▶ classify_risk
      │                                                                          │
      │                                                                          ▼
      │                                                                  detect_duplicates
      │                                                                          │
      │                                                                          ▼
      │                                                                  suggest_root_cause
      │                                                                          │
      │                                                                          ▼
      │                                                                    suggest_capa
      │                                                                          │
      │                                                                          ▼
      │                                                                      summarize
      │                                                                          │
      │                                                                          ▼
      │                                                        compose_new_complaint_reply ▶ END
      │
      ├──"correction"──▶ apply_correction ▶ END
      │
      └──"chit_chat"───▶ chit_chat ▶ END

Every node is a small pure-ish function in nodes.py; this file only wires them.
"""
from langgraph.graph import StateGraph, END

from app.agent.state import AgentState
from app.agent import nodes


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("classify_intent", nodes.classify_intent)
    graph.add_node("extract_fields", nodes.extract_fields)
    graph.add_node("check_completeness", nodes.check_completeness)
    graph.add_node("classify_risk", nodes.classify_risk)
    graph.add_node("detect_duplicates", nodes.detect_duplicates)
    graph.add_node("suggest_root_cause", nodes.suggest_root_cause)
    graph.add_node("suggest_capa", nodes.suggest_capa)
    graph.add_node("summarize", nodes.summarize)
    graph.add_node("compose_new_complaint_reply", nodes.compose_new_complaint_reply)
    graph.add_node("apply_correction", nodes.apply_correction)
    graph.add_node("chit_chat", nodes.chit_chat)

    graph.set_entry_point("classify_intent")

    graph.add_conditional_edges(
        "classify_intent",
        nodes.route_by_intent,
        {
            "new_complaint": "extract_fields",
            "correction": "apply_correction",
            "chit_chat": "chit_chat",
        },
    )

    # Linear pipeline for a brand-new complaint
    graph.add_edge("extract_fields", "check_completeness")
    graph.add_edge("check_completeness", "classify_risk")
    graph.add_edge("classify_risk", "detect_duplicates")
    graph.add_edge("detect_duplicates", "suggest_root_cause")
    graph.add_edge("suggest_root_cause", "suggest_capa")
    graph.add_edge("suggest_capa", "summarize")
    graph.add_edge("summarize", "compose_new_complaint_reply")
    graph.add_edge("compose_new_complaint_reply", END)

    graph.add_edge("apply_correction", END)
    graph.add_edge("chit_chat", END)

    return graph.compile()


# Compiled once at import time and reused for every request.
compiled_graph = build_graph()


def run_agent(
    session_id: str,
    user_message: str,
    existing_fields: dict | None = None,
    attachment_text: str | None = None,
    existing_complaints: list[dict] | None = None,
) -> AgentState:
    initial_state: AgentState = {
        "session_id": session_id,
        "user_message": user_message,
        "attachment_text": attachment_text,
        "existing_fields": existing_fields or {},
        "existing_complaints": existing_complaints or [],
        "trace": [],
    }
    final_state = compiled_graph.invoke(initial_state)
    return final_state
