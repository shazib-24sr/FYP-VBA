import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import SignIn from '../src/components/Auth/SignIn';
import SignUp from '../src/components/Auth/SignUp';
import DashboardPage from "../src/pages/DashboardPage"
import UploadPage from './pages/upload';
import ViewViolatedFrame from '../src/components/Dashboard/ViewFrameButton'
import SearchPage from './pages/search';
import Chat from './pages/chatbot';
import VehicleHistoryPage from './pages/vehiclehistory';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<SignIn />} />
        <Route path="/signup" element={<SignUp />} />
        <Route path="/upload" element={<UploadPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/search" element={<SearchPage />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/vehicleHistory" element={<VehicleHistoryPage />} />
        <Route path="/violations" element={<ViewViolatedFrame />} />
      </Routes>
    </Router>
  );
}

export default App;
