import { Navigate, Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { AboutPage } from "./pages/AboutPage";
import { AccountPage } from "./pages/AccountPage";
import { ContactPage } from "./pages/ContactPage";
import { DownloadPage } from "./pages/DownloadPage";
import { GuidesPage } from "./pages/GuidesPage";
import { Home } from "./pages/Home";
import { LadderPage } from "./pages/LadderPage";
import { LegalPage } from "./pages/LegalPage";
import { MediaPage } from "./pages/MediaPage";
import { RoadmapPage } from "./pages/RoadmapPage";

export function App() {
  return <Routes><Route element={<Layout />}><Route index element={<Home />} /><Route path="ladder" element={<LadderPage />} /><Route path="download" element={<DownloadPage />} /><Route path="guides" element={<GuidesPage />} /><Route path="guides/:slug" element={<GuidesPage />} /><Route path="about" element={<AboutPage />} /><Route path="roadmap" element={<RoadmapPage />} /><Route path="media" element={<MediaPage />} /><Route path="community" element={<Navigate to="/contact" replace />} /><Route path="contact" element={<ContactPage />} /><Route path="account" element={<AccountPage />} /><Route path="privacy" element={<LegalPage type="privacy" />} /><Route path="terms" element={<LegalPage type="terms" />} /><Route path="*" element={<Navigate to="/" replace />} /></Route></Routes>;
}

