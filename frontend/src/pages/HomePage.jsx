import React from "react";
import { useEffect, useState } from "react";
import { Activity, Database, FileText, ShieldCheck } from "lucide-react";

import { getHealth } from "../services/api";

const foundations = [
  {
    title: "FastAPI backend",
    description: "API app, CORS, settings, health check, and SQLite connection are ready.",
    icon: Activity,
  },
  {
    title: "SQLite foundation",
    description: "SQLAlchemy is configured so auth, documents, chats, memory, and progress can be added cleanly.",
    icon: Database,
  },
  {
    title: "React frontend",
    description: "Vite app shell, navigation, API client, and responsive UI base are in place.",
    icon: FileText,
  },
  {
    title: "Security direction",
    description: "Environment variables and ownership-aware architecture are established from the first phase.",
    icon: ShieldCheck,
  },
];

export default function HomePage() {
  const [health, setHealth] = useState({ status: "checking", database: "checking" });

  useEffect(() => {
    getHealth()
      .then(setHealth)
      .catch(() => setHealth({ status: "offline", database: "unavailable" }));
  }, []);

  return (
    <div className="dashboard">
      <section className="hero">
        <div>
          <p className="eyebrow">Final-year B.E. Computer Science Project</p>
          <h1>AI Learning & Study Assistant</h1>
          <p>
            A production-minded foundation for a personalized study platform with RAG, memory,
            AI tools, quizzes, progress tracking, and study planning.
          </p>
        </div>
        <div className="status-card">
          <span className={`status-dot ${health.status === "ok" ? "online" : ""}`} />
          <strong>Backend: {health.status}</strong>
          <small>Database: {health.database}</small>
        </div>
      </section>

      <section className="grid">
        {foundations.map((item) => {
          const Icon = item.icon;
          return (
            <article className="feature-card" key={item.title}>
              <Icon size={24} />
              <h2>{item.title}</h2>
              <p>{item.description}</p>
            </article>
          );
        })}
      </section>
    </div>
  );
}
