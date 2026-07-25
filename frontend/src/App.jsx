import React from "react";
import { Routes, Route, NavLink } from "react-router-dom";
import DashboardPage from "./features/dashboard/DashboardPage";
import LogComplaintPage from "./features/complaints/LogComplaintPage";
import "./App.css";

export default function App() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="sidebar-logo">A</div>
          <div>
            <div className="sidebar-brand-title">AIVOA</div>
            <div className="sidebar-brand-sub">QMS Suite</div>
          </div>
        </div>
        <nav className="sidebar-nav">
          <NavLink to="/" end className={({ isActive }) => (isActive ? "nav-item active" : "nav-item")}>
            Dashboard
          </NavLink>
          <NavLink to="/log-complaint" className={({ isActive }) => (isActive ? "nav-item active" : "nav-item")}>
            Log Customer Complaint
          </NavLink>
        </nav>
        <div className="sidebar-footer">API &amp; FDF Quality Assurance</div>
      </aside>

      <main className="main-content">
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/log-complaint" element={<LogComplaintPage />} />
        </Routes>
      </main>
    </div>
  );
}
