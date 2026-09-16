import React from "react";
import { Routes, Route, useLocation } from "react-router-dom";

import Navbar from "./components/Navbar";
import SpaceBackground from "./components/SpaceBackground";

import Overview from "./pages/Overview";
import ThermalMapPage from "./pages/ThermalMapPage";
import Events from "./pages/Events";
import Analysis from "./pages/Analysis";
import DistrictIntelligence from "./pages/DistrictIntelligence";
import Reports from "./pages/Reports";

import "./App.css";

function App() {
  const location = useLocation();

  React.useEffect(() => {
    if (!location.hash) {
      window.scrollTo({
        top: 0,
        behavior: "smooth",
      });
      return;
    }

    const id = location.hash.substring(1);

    const timer = setTimeout(() => {
      const element = document.getElementById(id);

      if (element) {
        element.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }
    }, 100);

    return () => clearTimeout(timer);
  }, [location.pathname, location.hash]);

  return (
    <div className="app">
      <SpaceBackground />

      <Navbar />

      <main className="main-content">
        <Routes>
          <Route path="/" element={<Overview />} />
          <Route path="/map" element={<ThermalMapPage />} />
          <Route path="/events" element={<Events />} />
          <Route path="/analysis" element={<Analysis />} />
          <Route path="/intelligence" element={<DistrictIntelligence />} />
          <Route path="/reports" element={<Reports />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;