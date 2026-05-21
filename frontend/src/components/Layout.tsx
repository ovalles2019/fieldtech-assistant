import { NavLink, Outlet } from "react-router-dom";
import { BookOpen, MessageSquare, QrCode, Ticket } from "lucide-react";
import { useOnline } from "../hooks/useOnline";

export default function Layout() {
  const online = useOnline();

  return (
    <>
      {!online && (
        <div className="offline-banner">Offline — showing cached answers when available</div>
      )}
      <div className="app-shell">
        <header style={{ marginBottom: "1rem" }}>
          <h1 style={{ margin: 0, fontSize: "1.35rem" }}>FieldTech Assistant</h1>
          <p style={{ margin: "0.25rem 0 0", color: "var(--muted)", fontSize: "0.9rem" }}>
            Manuals · Wiring · Service history · On-site RAG
          </p>
        </header>
        <Outlet />
      </div>
      <nav className="nav-bottom">
        <div className="nav-bottom-inner">
          <NavLink to="/" className={({ isActive }) => `nav-item${isActive ? " active" : ""}`} end>
            <MessageSquare size={20} />
            Ask
          </NavLink>
          <NavLink to="/scan" className={({ isActive }) => `nav-item${isActive ? " active" : ""}`}>
            <QrCode size={20} />
            Scan
          </NavLink>
          <NavLink to="/assets" className={({ isActive }) => `nav-item${isActive ? " active" : ""}`}>
            <BookOpen size={20} />
            Assets
          </NavLink>
          <NavLink to="/tickets" className={({ isActive }) => `nav-item${isActive ? " active" : ""}`}>
            <Ticket size={20} />
            Tickets
          </NavLink>
        </div>
      </nav>
    </>
  );
}
