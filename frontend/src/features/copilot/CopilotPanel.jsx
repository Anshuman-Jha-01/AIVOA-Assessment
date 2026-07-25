import React, { useRef, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { addUserMessage, addFileMessage, sendCopilotMessage, uploadCopilotFile } from "./copilotSlice";
import "./CopilotPanel.css";

export default function CopilotPanel() {
  const dispatch = useDispatch();
  const { messages, loading } = useSelector((s) => s.copilot);
  const [input, setInput] = useState("");
  const fileInputRef = useRef(null);
  const scrollRef = useRef(null);

  const handleSend = () => {
    const text = input.trim();
    if (!text || loading) return;
    dispatch(addUserMessage(text));
    dispatch(sendCopilotMessage(text));
    setInput("");
    setTimeout(() => scrollRef.current?.scrollTo(0, scrollRef.current.scrollHeight), 50);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    dispatch(addFileMessage(file.name));
    dispatch(uploadCopilotFile(file));
    e.target.value = "";
  };

  return (
    <div className="copilot-panel">
      <div className="copilot-header">
        <div className="copilot-icon">⚗️</div>
        <div>
          <div className="copilot-title">AIVOA Copilot</div>
          <div className="copilot-subtitle">Drop complaint files or paste text below.</div>
        </div>
        <span className={`copilot-status-dot ${loading ? "busy" : "idle"}`} />
      </div>

      <div className="copilot-messages" ref={scrollRef}>
        {messages.map((m, i) => (
          <div key={i} className={`msg-row ${m.role}`}>
            {m.isFile ? (
              <div className="msg-file-bubble">
                <span className="file-icon">📄</span>
                <div>
                  <div className="file-name">{m.content}</div>
                  <div className="file-type">Document</div>
                </div>
              </div>
            ) : (
              <div className={`msg-bubble ${m.role}`}>{m.content}</div>
            )}
          </div>
        ))}
        {loading && (
          <div className="msg-row assistant">
            <div className="msg-bubble assistant typing">
              <span className="dot" />
              <span className="dot" />
              <span className="dot" />
            </div>
          </div>
        )}
      </div>

      <div className="copilot-input-row">
        <button className="attach-btn" onClick={() => fileInputRef.current?.click()} title="Attach file">
          📎
        </button>
        <input
          type="file"
          ref={fileInputRef}
          style={{ display: "none" }}
          accept=".pdf,.txt,.eml"
          onChange={handleFileSelect}
        />
        <input
          type="text"
          placeholder="Type a message or paste a complaint..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button className="send-btn" onClick={handleSend} disabled={loading || !input.trim()}>
          ✓
        </button>
      </div>
      <div className="copilot-footer">POWERED BY LANGGRAPH</div>
    </div>
  );
}
