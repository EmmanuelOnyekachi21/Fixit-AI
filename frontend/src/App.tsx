import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import AnalysisProgress from './pages/AnalysisProgress';
import Vulnerabilities from './pages/Vulnerabilities';
import Settings from './pages/Settings';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { useState } from 'react';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <Router>
      <div className="min-h-screen bg-gray-950 text-gray-100">
        <Navbar onMenuClick={() => setSidebarOpen(true)} />
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        
        <div className="lg:pl-64 flex flex-col min-h-screen">
          <main className="flex-1">
            <div className="py-8">
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
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