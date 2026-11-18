import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Sidebar } from './components/Sidebar';
import { TopNav } from './components/TopNav';
import { ExplorePage } from './pages/ExplorePage';
import { CreateStudioPage } from './pages/CreateStudioPage';
import { PromptLabPage } from './pages/PromptLabPage';
import { EvaluationDashboardPage } from './pages/EvaluationDashboardPage';
import { ProjectsPage } from './pages/ProjectsPage';
import { DatasetStudioPage } from './pages/DatasetStudioPage';
import { SettingsPage } from './pages/SettingsPage';
import { api } from './services/api';
import { SystemStatus } from './types';

export function App() {
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const fetchStatus = async () => {
    try {
      const data = await api.getSystemStatus();
      setSystemStatus(data);
    } catch (err) {
      console.warn('System status check offline', err);
      setSystemStatus({
        mode: 'demo',
        database_connected: true,
        database_type: 'LocalJsonStorage',
        services: {},
        version: '1.0.0'
      });
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-[#090A0C] text-[#E2E8F0] flex flex-col font-sans selection:bg-cyan-500/30 selection:text-cyan-200">
        {/* Persistent Desktop Sidebar */}
        <Sidebar />

        {/* Persistent Top Navigation Bar */}
        <TopNav
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
        />

        {/* Main Content Area */}
        <main className="flex-1 pl-64 pt-16 min-h-screen">
          <div className="p-8">
            <Routes>
              <Route path="/" element={<ExplorePage searchQuery={searchQuery} />} />
              <Route path="/create" element={<CreateStudioPage />} />
              <Route path="/projects" element={<ProjectsPage />} />
              <Route path="/settings" element={<SettingsPage systemStatus={systemStatus} onRefreshStatus={fetchStatus} />} />
              <Route path="/prompt-lab" element={<PromptLabPage />} />
              <Route path="/evaluation" element={<EvaluationDashboardPage />} />
              <Route path="/datasets" element={<DatasetStudioPage />} />
            </Routes>
          </div>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
