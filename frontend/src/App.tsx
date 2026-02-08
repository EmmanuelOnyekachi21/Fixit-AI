import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import ModeSelector from './pages/ModeSelector';
import Dashboard from './pages/Dashboard';
import AnalysisProgress from './pages/AnalysisProgress';
import Vulnerabilities from './pages/Vulnerabilities';
import Settings from './pages/Settings';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { useState, useEffect } from 'react';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [mode, setMode] = useState<'demo' | 'real' | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user has selected a mode
    const savedMode = localStorage.getItem('fixit_mode') as 'demo' | 'real' | null;
    setMode(savedMode);
    setLoading(false);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-400">Loading Fixit...</p>
        </div>
      </div>
    );
  }

  // If no mode selected, show mode selector (landing page)
  if (!mode) {
    return (
      <Router>
        <Routes>
          <Route path="/" element={<ModeSelector />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    );
  }

  // Mode selected - show main app
  return (
    <Router>
      <div className="min-h-screen bg-gray-950 text-gray-100">
        <Navbar onMenuClick={() => setSidebarOpen(true)} />
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        
        <div className="lg:pl-64 flex flex-col min-h-screen">
          <main className="flex-1">
            <div className="py-8">
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                {/* Mode Indicator */}
                <div className="mb-6 flex items-center justify-between bg-gray-800/50 border border-gray-700 rounded-lg px-4 py-3">
                  <div className="flex items-center gap-2">
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                      mode === 'demo' 
                        ? 'bg-blue-500/20 text-blue-400' 
                        : 'bg-purple-500/20 text-purple-400'
                    }`}>
                      {mode === 'demo' ? '📺 Demo Mode' : '⚡ Real-Time Mode'}
                    </span>
                    <span className="text-xs text-gray-500">
                      {mode === 'demo' 
                        ? 'Using simulated data' 
                        : 'Connected to real APIs'}
                    </span>
                  </div>
                  <button
                    onClick={() => {
                      localStorage.removeItem('fixit_mode');
                      setMode(null);
                      window.location.href = '/';
                    }}
                    className="text-xs text-gray-400 hover:text-gray-300 transition-colors px-3 py-1 hover:bg-gray-700 rounded"
                  >
                    Switch Mode
                  </button>
                </div>

                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  {/* :id accepts any string including UUIDs from backend */}
                  <Route path="/analysis/:id" element={<AnalysisProgress />} />
                  <Route path="/vulnerabilities" element={<Vulnerabilities />} />
                  <Route path="/settings" element={<Settings />} />
                </Routes>
              </div>
            </div>
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App;