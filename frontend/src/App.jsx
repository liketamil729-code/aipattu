import React from "react";
import { Routes, Route, NavLink } from "react-router-dom";
import { BookOpen, BrainCircuit, LayoutDashboard, MessageSquareText } from "lucide-react";

import ChatPage from "./pages/ChatPage.jsx";
import HomePage from "./pages/HomePage.jsx";
import MaterialsPage from "./pages/MaterialsPage.jsx";
import ProgressPage from "./pages/ProgressPage.jsx";

const navItems = [
  { to: "/", label: "Overview", icon: LayoutDashboard },
  { to: "/chat", label: "AI Chat", icon: MessageSquareText },
  { to: "/materials", label: "Materials", icon: BookOpen },
  { to: "/progress", label: "Progress", icon: BrainCircuit },
];

export default function App() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">AI</span>
          <div>
            <strong>Study Assistant</strong>
            <small>RAG + Memory + Agent</small>
          </div>
        </div>
        <nav>
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink key={item.to} to={item.to} className={({ isActive }) => (isActive ? "active" : "")}>
                <Icon size={18} />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>
      </aside>

      <main className="main-content">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/materials" element={<MaterialsPage />} />
          <Route path="/progress" element={<ProgressPage />} />
        </Routes>
      </main>
    </div>
  );
}
