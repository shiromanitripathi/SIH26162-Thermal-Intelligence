import { Routes, Route } from "react-router-dom";

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

          <Route
            path="/intelligence"
            element={<DistrictIntelligence />}
          />

          <Route path="/reports" element={<Reports />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;