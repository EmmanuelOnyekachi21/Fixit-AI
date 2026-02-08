import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Zap, Play, Sparkles } from 'lucide-react';

export default function ModeSelector() {
  const navigate = useNavigate();
  const [selectedMode, setSelectedMode] = useState<'demo' | 'real' | null>(null);

  const handleDemoMode = () => {
    localStorage.setItem('fixit_mode', 'demo');
    navigate('/');
    window.location.reload();
  };

  const handleRealMode = () => {
    localStorage.setItem('fixit_mode', 'real');
    // Navigate to settings for real-time mode setup
    navigate('/settings');
    window.location.reload();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black flex items-center justify-center p-4">
      <div className="max-w-6xl w-full">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-white mb-4">
            🛠️ Welcome to Fixit
          </h1>
          <p className="text-xl text-gray-400">
            Choose how you'd like to experience the autonomous security agent
          </p>
        </div>

        {/* Mode Selection Cards */}
        <div className="grid md:grid-cols-2 gap-8 mb-12">
          {/* Demo Mode Card */}
          <div
            onClick={handleDemoMode}
            className={`relative group cursor-pointer transition-all duration-300 ${
              selectedMode === 'demo' ? 'scale-105' : 'hover:scale-102'
            }`}
          >
            <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-blue-400 rounded-2xl blur-xl opacity-0 group-hover:opacity-75 transition-opacity duration-300"></div>
            <div className="relative bg-gray-800 border-2 border-gray-700 hover:border-blue-500 rounded-2xl p-8 transition-all duration-300">
              <div className="flex items-center justify-center w-16 h-16 bg-blue-500/10 rounded-xl mb-6">
                <Play className="w-8 h-8 text-blue-400" />
              </div>
              
              <h2 className="text-2xl font-bold text-white mb-3">Demo Mode</h2>
              
              <p className="text-gray-400 mb-6">
                Experience Fixit with pre-generated mock data. Perfect for exploring the UI and understanding the workflow.
              </p>

              <div className="space-y-3 mb-8">
                <div className="flex items-center gap-3 text-sm text-gray-300">
                  <span className="text-green-400">✓</span>
                  <span>No API keys required</span>
                </div>
                <div className="flex items-center gap-3 text-sm text-gray-300">
                  <span className="text-green-400">✓</span>
                  <span>Instant results</span>
                </div>
                <div className="flex items-center gap-3 text-sm text-gray-300">
                  <span className="text-green-400">✓</span>
                  <span>See the full workflow</span>
                </div>
                <div className="flex items-center gap-3 text-sm text-gray-300">
                  <span className="text-green-400">✓</span>
                  <span>Real-time UI updates</span>
                </div>
              </div>

              <button
                onClick={handleDemoMode}
                className="w-full px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors duration-200"
              >
                Start Demo
              </button>

              <p className="text-xs text-gray-500 mt-4 text-center">
                Best for: Judges, first-time users, UI exploration
              </p>
            </div>
          </div>

          {/* Real Mode Card */}
          <div
            onClick={handleRealMode}
            className={`relative group cursor-pointer transition-all duration-300 ${
              selectedMode === 'real' ? 'scale-105' : 'hover:scale-102'
            }`}
          >
            <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-pink-400 rounded-2xl blur-xl opacity-0 group-hover:opacity-75 transition-opacity duration-300"></div>
            <div className="relative bg-gray-800 border-2 border-gray-700 hover:border-purple-500 rounded-2xl p-8 transition-all duration-300">
              <div className="flex items-center justify-center w-16 h-16 bg-purple-500/10 rounded-xl mb-6">
                <Zap className="w-8 h-8 text-purple-400" />
              </div>
              
              <h2 className="text-2xl font-bold text-white mb-3">Real-Time Mode</h2>
              
              <p className="text-gray-400 mb-6">
                Connect your own GitHub and Gemini API keys to analyze real repositories and create actual pull requests.
              </p>

              <div className="space-y-3 mb-8">
                <div className="flex items-center gap-3 text-sm text-gray-300">
                  <span className="text-green-400">✓</span>
                  <span>Real vulnerability detection</span>
                </div>
                <div className="flex items-center gap-3 text-sm text-gray-300">
                  <span className="text-green-400">✓</span>
                  <span>Actual PR creation on GitHub</span>
                </div>
                <div className="flex items-center gap-3 text-sm text-gray-300">
                  <span className="text-green-400">✓</span>
                  <span>Full system capabilities</span>
                </div>
                <div className="flex items-center gap-3 text-sm text-gray-300">
                  <span className="text-green-400">✓</span>
                  <span>Verify-first workflow in action</span>
                </div>
              </div>

              <button
                onClick={handleRealMode}
                className="w-full px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-lg transition-colors duration-200 flex items-center justify-center gap-2"
              >
                <Sparkles className="w-4 h-4" />
                Start Real-Time
              </button>

              <p className="text-xs text-gray-500 mt-4 text-center">
                Best for: Developers, advanced testing, production use
              </p>
            </div>
          </div>
        </div>

        {/* Info Section */}
        <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-8">
          <h3 className="text-lg font-semibold text-white mb-4">How to Get Started</h3>
          
          <div className="grid md:grid-cols-2 gap-8">
            <div>
              <h4 className="text-blue-400 font-semibold mb-3">Demo Mode</h4>
              <p className="text-gray-400 text-sm">
                Click "Start Demo" to explore Fixit with simulated data. No setup required. Perfect for understanding how the system works.
              </p>
            </div>
            
            <div>
              <h4 className="text-purple-400 font-semibold mb-3">Real-Time Mode</h4>
              <p className="text-gray-400 text-sm">
                You'll be prompted to enter your Gemini API key and GitHub token. Get them from:
              </p>
              <ul className="text-gray-400 text-sm mt-2 space-y-1">
                <li>• Gemini: <span className="text-blue-400">aistudio.google.com/app/apikey</span></li>
                <li>• GitHub: <span className="text-blue-400">github.com/settings/tokens</span></li>
              </ul>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-12 text-gray-500 text-sm">
          <p>Built with Gemini 3 • Django • React • PostgreSQL</p>
        </div>
      </div>
    </div>
  );
}
