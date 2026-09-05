import React from "react";
import { AlertTriangle, BarChart3, CalendarClock, CheckCircle2 } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const emptyChartData = [
  { topic: "No data", score: 0 },
];

export default function ProgressPage() {
  return (
    <div className="workspace-page">
      <section className="page-header">
        <div>
          <p className="eyebrow">Learning analytics</p>
          <h1>Progress Tracking</h1>
          <p>Mastery indicators, weak topics, quiz scores, and study streaks will be calculated from real activity.</p>
        </div>
      </section>

      <section className="metric-grid">
        <article className="metric-card">
          <CheckCircle2 size={22} />
          <span>Completed Topics</span>
          <strong>0</strong>
        </article>
        <article className="metric-card">
          <BarChart3 size={22} />
          <span>Average Quiz Score</span>
          <strong>0%</strong>
        </article>
        <article className="metric-card">
          <AlertTriangle size={22} />
          <span>Weak Topics</span>
          <strong>0</strong>
        </article>
        <article className="metric-card">
          <CalendarClock size={22} />
          <span>Study Streak</span>
          <strong>0 days</strong>
        </article>
      </section>

      <section className="analytics-grid">
        <article className="chart-panel">
          <h2>Topic Mastery</h2>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={emptyChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="topic" />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Bar dataKey="score" fill="#195c44" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </article>

        <article className="empty-state progress-empty">
          <AlertTriangle size={42} />
          <h2>No progress records yet</h2>
          <p>Complete quizzes and study sessions to detect weak topics and generate a personalized study plan.</p>
        </article>
      </section>
    </div>
  );
}
