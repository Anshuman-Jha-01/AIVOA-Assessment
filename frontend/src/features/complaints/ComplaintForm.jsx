import React from "react";
import { useDispatch, useSelector } from "react-redux";
import { setField, commitComplaint, resetDraft } from "./complaintDraftSlice";
import "./ComplaintForm.css";

function Field({ label, value, onChange, placeholder }) {
  return (
    <div className="field">
      <label>{label}</label>
      <input
        type="text"
        value={value || ""}
        placeholder={placeholder || "Awaiting AI extraction..."}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  );
}

export default function ComplaintForm() {
  const dispatch = useDispatch();
  const { fields, assessment, duplicates, status, committing, committed } = useSelector(
    (s) => s.complaintDraft
  );

  const set = (field) => (value) => dispatch(setField({ field, value }));

  const canCommit = status === "READY_TO_COMMIT" && !committing;

  if (committed) {
    return (
      <div className="committed-state">
        <h2>✅ Complaint Committed to QMS Ledger</h2>
        <p>
          <strong>{committed.complaint_number}</strong> has been saved. You can log another complaint below.
        </p>
        <button className="btn-secondary" onClick={() => dispatch(resetDraft())}>
          Log Another Complaint
        </button>
      </div>
    );
  }

  return (
    <div className="complaint-form">
      <section className="form-section">
        <h3>1. Origin &amp; Customer Details</h3>
        <div className="field-grid">
          <Field label="Complaint Source" value={fields.complaint_source} onChange={set("complaint_source")} />
          <Field label="Customer Name" value={fields.customer_name} onChange={set("customer_name")} />
        </div>
      </section>

      <section className="form-section">
        <h3>2. Product &amp; Batch Identification</h3>
        <div className="field-grid">
          <Field label="Product Name (API/FDF)" value={fields.product_name} onChange={set("product_name")} />
          <Field label="Product Strength" value={fields.product_strength} onChange={set("product_strength")} />
          <Field label="Batch / Lot Number" value={fields.batch_lot_number} onChange={set("batch_lot_number")} />
          <Field label="Affected Quantity" value={fields.affected_quantity} onChange={set("affected_quantity")} />
          <Field label="Manufacturing Date" value={fields.manufacturing_date} onChange={set("manufacturing_date")} />
          <Field label="Expiry Date" value={fields.expiry_date} onChange={set("expiry_date")} />
        </div>
      </section>

      <section className="form-section">
        <h3>3. Facility &amp; Material Impact</h3>
        <div className="field-grid">
          <Field
            label="Originating Site Block"
            value={fields.originating_site_block}
            onChange={set("originating_site_block")}
            placeholder="Awaiting AI classification..."
          />
          <Field
            label="Impacted Non-Product Materials (NPM)"
            value={fields.impacted_npm}
            onChange={set("impacted_npm")}
            placeholder="e.g., Primary packaging..."
          />
        </div>
      </section>

      <section className="form-section">
        <h3>4. Defect Analysis</h3>
        <div className="field">
          <label>Complaint Category</label>
          <input
            type="text"
            value={fields.complaint_category || ""}
            placeholder="Awaiting AI classification..."
            onChange={(e) => set("complaint_category")(e.target.value)}
          />
        </div>
        <div className="field">
          <label>Complaint Description</label>
          <textarea
            rows={3}
            value={fields.complaint_description || ""}
            placeholder="AI will synthesize the complaint into a formal QMS description..."
            onChange={(e) => set("complaint_description")(e.target.value)}
          />
        </div>

        {(assessment.ai_severity_suggested || assessment.ai_initial_risk_assessment) && (
          <div className="ai-risk-panel">
            <div className="ai-risk-title">🛡️ AI Copilot Risk Assessment</div>
            <div className="field-grid">
              <div className="field">
                <label>Severity (Suggested)</label>
                <input type="text" value={assessment.ai_severity_suggested || ""} readOnly />
              </div>
              <div className="field">
                <label>Suggested Next Action</label>
                <input type="text" value={assessment.ai_suggested_next_action || ""} readOnly />
              </div>
            </div>
            <div className="field">
              <label>Initial Risk Assessment</label>
              <textarea rows={2} value={assessment.ai_initial_risk_assessment || ""} readOnly />
            </div>

            {assessment.ai_root_cause_suggestion && (
              <div className="field">
                <label>Suggested Root Cause</label>
                <textarea rows={2} value={assessment.ai_root_cause_suggestion} readOnly />
              </div>
            )}
            {assessment.ai_capa_suggestion && (
              <div className="field">
                <label>Suggested CAPA</label>
                <textarea rows={2} value={assessment.ai_capa_suggestion} readOnly />
              </div>
            )}
            {assessment.ai_summary && (
              <div className="field">
                <label>AI Summary</label>
                <textarea rows={2} value={assessment.ai_summary} readOnly />
              </div>
            )}
            {assessment.ai_completeness_notes && (
              <div className="completeness-note">⚠️ {assessment.ai_completeness_notes}</div>
            )}

            {duplicates && duplicates.length > 0 && (
              <div className="duplicates-note">
                <strong>Possible duplicates:</strong>
                <ul>
                  {duplicates.map((d) => (
                    <li key={d.complaint_id}>
                      {d.complaint_number} — {(d.similarity_score * 100).toFixed(0)}% match: {d.rationale}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        <button className="btn-commit" disabled={!canCommit} onClick={() => dispatch(commitComplaint())}>
          {committing ? "Committing..." : "Commit to QMS Ledger"}
        </button>
      </section>
    </div>
  );
}
