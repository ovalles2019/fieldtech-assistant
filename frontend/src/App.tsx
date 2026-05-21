import { useEffect } from "react";
import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import AskPage from "./pages/AskPage";
import ScanPage from "./pages/ScanPage";
import AssetsPage from "./pages/AssetsPage";
import TicketsPage from "./pages/TicketsPage";
import { initAuth } from "./lib/api";

export default function App() {
  useEffect(() => {
    initAuth();
  }, []);

  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<AskPage />} />
        <Route path="scan" element={<ScanPage />} />
        <Route path="assets" element={<AssetsPage />} />
        <Route path="tickets" element={<TicketsPage />} />
      </Route>
    </Routes>
  );
}
