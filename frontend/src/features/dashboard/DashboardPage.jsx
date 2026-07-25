import React, { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { Link } from "react-router-dom";
import { fetchComplaints, fetchDashboardStats } from "./dashboardSlice";
import "./DashboardPage.css";

const SEVERITY_CLASS = {
  Critical: "sev-critical",
  Major: "sev-major",
  Minor: "sev-minor",
};

export default function DashboardPage() {
  const dispatch = useDispatch();
  const { complaints, stats, loading } = useSelector((s) => s.dashboard);

  useEffect(() => {
    dispatch(fetchComplaints());
    dispatch(fetchDashboardStats());
  }, [dispatch]);

  return (
    <div className="dashboard-page">
      <header className="dashboard-header">
        <div>
          <h1>Complaints Console</h1>
          <p className="subtitle">API &amp; FDF Quality Assurance Module</p>
        </div>
        <Link to="/log-complaint" className="btn-primary-link">
          + Log Customer Complaint
        </Link>
      </header>

      <div className="kpi-row">
        <KpiCard label="Total Complaints" value={stats.total} />
        <KpiCard label="Pending Triage" value={stats.pending_triage} accent="warning" />
        <KpiCard label="Ready to Commit" value={stats.ready_to_commit} accent="primary" />
        <KpiCard label="Committed" value={stats.committed} accent="success" />
        <KpiCard label="Critical" value={stats.critical} accent="critical" />
      </div>

      <div className="table-card">
        <table>
          <thead>
            <tr>
              <th>Complaint #</th>
              <th>Product</th>
              <th>Batch/Lot</th>
              <th>Customer</th>
              <th>Category</th>
              <th>Severity</th>
              <th>Status</th>
              <th>Logged</th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr>
                <td colSpan={8} className="empty-state">Loading...</td>
              </tr>
            )}
            {!loading && complaints.length === 0 && (
              <tr>
                <td colSpan={8} className="empty-state">
                  No complaints logged yet. Click "Log Customer Complaint" to get started.
                </td>
              </tr>
            )}
            {complaints.map((c) => (
              <tr key={c.id}>
                <td className="mono">{c.complaint_number}</td>
                <td>{c.product_name || "—"}</td>
                <td className="mono">{c.batch_lot_number || "—"}</td>
                <td>{c.customer_name || "—"}</td>
                <td>{c.complaint_category || "—"}</td>
                <td>
                  {c.ai_severity_suggested ? (
                    <span className={`sev-badge ${SEVERITY_CLASS[c.ai_severity_suggested] || ""}`}>
                      {c.ai_severity_suggested}
                    </span>
                  ) : (
                    "—"
                  )}
                </td>
                <td>
                  <span className="status-pill">{c.status.replaceAll("_", " ")}</span>
                </td>
                <td>{new Date(c.created_at).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function KpiCard({ label, value, accent }) {
  return (
    <div className={`kpi-card ${accent ? "accent-" + accent : ""}`}>
      <div className="kpi-value">{value ?? 0}</div>
      <div className="kpi-label">{label}</div>
    </div>
  );
}
