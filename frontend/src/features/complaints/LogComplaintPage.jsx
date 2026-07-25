import React from "react";
import { useSelector } from "react-redux";
import ComplaintForm from "./ComplaintForm";
import CopilotPanel from "../copilot/CopilotPanel";
import "./LogComplaintPage.css";

const STATUS_LABEL = {
  PENDING_TRIAGE: { text: "Pending Triage", className: "badge-warning" },
  READY_TO_COMMIT: { text: "Ready to Commit", className: "badge-success" },
  COMMITTED: { text: "Committed", className: "badge-success" },
};

export default function LogComplaintPage() {
  const status = useSelector((s) => s.complaintDraft.status);
  const badge = STATUS_LABEL[status] || STATUS_LABEL.PENDING_TRIAGE;

  return (
    <div className="log-complaint-page">
      <header className="log-complaint-header">
        <div>
          <h1>Log Customer Complaint</h1>
          <p className="subtitle">API &amp; FDF Quality Assurance Module</p>
        </div>
        <span className={`status-badge ${badge.className}`}>
          <span className="status-dot" /> {badge.text}
        </span>
      </header>

      <div className="log-complaint-body">
        <div className="form-panel">
          <ComplaintForm />
        </div>
        <div className="copilot-panel-wrapper">
          <CopilotPanel />
        </div>
      </div>
    </div>
  );
}
