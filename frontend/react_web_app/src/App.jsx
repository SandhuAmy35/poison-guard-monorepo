import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import InteractiveBackground from './components/InteractiveBackground';
import LandingPage from './pages/LandingPage';
import UploadPage from './pages/UploadPage';
import ProcessingPage from './pages/ProcessingPage';
import VisualizationDashboard from './pages/VisualizationDashboard';

export default function App() {
  return (
    <div className="min-h-screen bg-transparent text-slate-100 font-sans overflow-hidden relative">
      <InteractiveBackground />
      <Router>
        <div className="relative z-10 w-full min-h-screen">
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/processing" element={<ProcessingPage />} />
            <Route path="/dashboard" element={<VisualizationDashboard />} />
          </Routes>
        </div>
      </Router>
    </div>
  );
}