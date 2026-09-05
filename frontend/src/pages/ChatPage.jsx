import React, { useEffect, useMemo, useState } from "react";
import { Bot, Copy, FileSearch, MessageSquarePlus, RefreshCcw, Send, SlidersHorizontal } from "lucide-react";

import { getDocuments, sendChatMessage } from "../services/api";

export default function ChatPage() {
  const [message, setMessage] = useState("");
  const [documents, setDocuments] = useState([]);
  const [subject, setSubject] = useState("");
  const [documentId, setDocumentId] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Upload study material first, then ask questions here. I will answer from retrieved document chunks and cite the exact sources once RAG is connected.",
    },
  ]);

  const subjects = useMemo(
    () => Array.from(new Set(documents.map((doc) => doc.subject).filter(Boolean))),
    [documents],
  );

  useEffect(() => {
    getDocuments().then(setDocuments).catch(() => setDocuments([]));
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();
    const trimmed = message.trim();
    if (!trimmed || isSending) return;

    setMessages((current) => [
      ...current,
      { role: "user", content: trimmed },
    ]);
    setMessage("");
    setIsSending(true);

    try {
      const result = await sendChatMessage({
        message: trimmed,
        subject,
        documentId: documentId ? Number(documentId) : null,
      });
      setMessages((current) => [
        ...current,
        { role: "assistant", content: result.answer, sources: result.sources },
      ]);
    } catch (error) {
      const detail = error.response?.data?.detail ?? "AI chat failed. Check backend logs and configuration.";
      setMessages((current) => [...current, { role: "assistant", content: detail, error: true }]);
    } finally {
      setIsSending(false);
    }
  }

  return (
    <div className="workspace-page chat-page">
      <section className="page-header">
        <div>
          <p className="eyebrow">RAG chat</p>
          <h1>AI Chat</h1>
          <p>Ask questions from uploaded notes, generate quizzes, or request a study plan through the agent.</p>
        </div>
        <button className="primary-action" type="button">
          <MessageSquarePlus size={18} />
          New Chat
        </button>
      </section>

      <div className="chat-layout">
        <aside className="tool-panel">
          <div className="panel-section">
            <h2>Study Filters</h2>
            <label>
              Subject
              <select value={subject} onChange={(event) => setSubject(event.target.value)}>
                <option value="">All subjects</option>
                {subjects.map((item) => (
                  <option key={item} value={item}>
                    {item}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Document
              <select value={documentId} onChange={(event) => setDocumentId(event.target.value)}>
                <option value="">All documents</option>
                {documents.map((doc) => (
                  <option key={doc.id} value={doc.id}>
                    {doc.original_filename}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <div className="panel-section">
            <h2>Agent Tools</h2>
            <div className="tool-list">
              <span><FileSearch size={16} /> Search materials</span>
              <span><SlidersHorizontal size={16} /> Route intent</span>
              <span><RefreshCcw size={16} /> Regenerate answer</span>
            </div>
          </div>
        </aside>

        <section className="chat-surface">
          <div className="messages">
            {messages.map((item, index) => (
              <article className={`message ${item.role}`} key={`${item.role}-${index}`}>
                {item.role === "assistant" && <Bot size={18} />}
                <div>
                  <p>{item.content}</p>
                  {item.sources?.length > 0 && (
                    <div className="source-list">
                      {item.sources.map((source, sourceIndex) => (
                        <span key={`${source.document_id}-${source.page_number}-${sourceIndex}`}>
                          {source.filename} - page {source.page_number}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                {item.role === "assistant" && (
                  <button className="icon-button" type="button" aria-label="Copy answer">
                    <Copy size={16} />
                  </button>
                )}
              </article>
            ))}
          </div>
          <form className="chat-composer" onSubmit={handleSubmit}>
            <input
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              placeholder={isSending ? "Thinking..." : "Ask about a topic from your notes..."}
              disabled={isSending}
            />
            <button type="submit" aria-label="Send message" disabled={isSending}>
              <Send size={18} />
            </button>
          </form>
        </section>
      </div>
    </div>
  );
}
