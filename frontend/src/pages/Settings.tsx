import { useState } from 'react';
import { Github, CheckCircle, XCircle, AlertTriangle, Save } from 'lucide-react';

export default function Settings() {
  const [githubToken, setGithubToken] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [username, setUsername] = useState('');
  const [isTesting, setIsTesting] = useState(false);
  const [maxFiles, setMaxFiles] = useState(100);
  const [autoCreatePRs, setAutoCreatePRs] = useState(true);
  const [checkpointInterval, setCheckpointInterval] = useState(10);
  const [saved, setSaved] = useState(false);

  const handleTestConnection = async () => {
    setIsTesting(true);
    // Simulate API call
    setTimeout(() => {
      if (githubToken.trim()) {
        setIsConnected(true);
        setUsername('demo-user');
      } else {
        setIsConnected(false);
        setUsername('');
      }
      setIsTesting(false);
    }, 1500);
  };

  const handleSaveSettings = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const handleClearSessions = () => {
    if (confirm('Are you sure you want to clear all old analysis sessions? This cannot be undone.')) {
      // Simulate clearing
      alert('Old sessions cleared successfully');
    }
  };

  const handleResetDatabase = () => {
    if (confirm('⚠️ WARNING: This will delete ALL data including repositories, vulnerabilities, and PRs. Are you absolutely sure?')) {
      if (confirm('This is your last chance. Type YES in the next prompt to confirm.')) {
        const confirmation = prompt('Type YES to confirm database reset:');
        if (confirmation === 'YES') {
          alert('Database reset successfully');
        }
      }
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white">Settings</h1>
        <p className="text-gray-400 mt-1">Configure FixIt security agent</p>
      </div>

      {/* GitHub Authentication */}
      <div className="bg-gray-900 border border-gray-800 rounded-lg p-6 shadow-xl">
        <div className="flex items-center gap-3 mb-6">
          <Github className="h-6 w-6 text-blue-500" />
          <h2 className="text-xl font-semibold text-white">GitHub Authentication</h2>
        </div>

        <div className="space-y-4">
          <div>
            <label htmlFor="github-token" className="block text-sm font-medium text-gray-300 mb-2">
              Personal Access Token
            </label>
            <input
              id="github-token"
              type="password"
              value={githubToken}
              onChange={(e) => setGithubToken(e.target.value)}
              placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
              className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            />
            <p className="text-xs text-gray-500 mt-2">
              Required scopes: repo, workflow, write:packages
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={handleTestConnection}
              disabled={isTesting || !githubToken.trim()}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
            >
              {isTesting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Testing...
                </>
              ) : (
                'Test Connection'
              )}
            </button>

            {isConnected && (
              <div className="flex items-center gap-2 text-green-400">
                <CheckCircle className="h-5 w-5" />
                <span className="text-sm">Connected as {username}</span>
              </div>
            )}

            {!isConnected && githubToken && !isTesting && (
              <div className="flex items-center gap-2 text-red-400">
                <XCircle className="h-5 w-5" />
                <span className="text-sm">Not connected</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Analysis Settings */}
      <div className="bg-gray-900 border border-gray-800 rounded-lg p-6 shadow-xl">
        <h2 className="text-xl font-semibold text-white mb-6">Analysis Settings</h2>

        <div className="space-y-6">
          <div>
            <label htmlFor="max-files" className="block text-sm font-medium text-gray-300 mb-2">
              Maximum Files to Analyze: {maxFiles}
            </label>
            <input
              id="max-files"
              type="range"
              min="10"
              max="1000"
              step="10"
              value={maxFiles}
              onChange={(e) => setMaxFiles(Number(e.target.value))}
              className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-600"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>10</span>
              <span>1000</span>
            </div>
          </div>

          <div className="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg border border-gray-700">
            <div>
              <h3 className="text-white font-medium">Auto-create Pull Requests</h3>
              <p className="text-sm text-gray-400 mt-1">
                Automatically create PRs for verified fixes
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={autoCreatePRs}
                onChange={(e) => setAutoCreatePRs(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-800 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <div>
            <label htmlFor="checkpoint" className="block text-sm font-medium text-gray-300 mb-2">
              Checkpoint Interval: Every {checkpointInterval} files
            </label>
            <input
              id="checkpoint"
              type="range"
              min="5"
              max="50"
              step="5"
              value={checkpointInterval}
              onChange={(e) => setCheckpointInterval(Number(e.target.value))}
              className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-600"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>5</span>
              <span>50</span>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Save progress periodically to resume if interrupted
            </p>
          </div>

          <button
            onClick={handleSaveSettings}
            className="flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors"
          >
            <Save className="h-5 w-5" />
            Save Settings
          </button>

          {saved && (
            <div className="flex items-center gap-2 text-green-400 animate-slide-up">
              <CheckCircle className="h-5 w-5" />
              <span className="text-sm">Settings saved successfully</span>
            </div>
          )}
        </div>
      </div>

      {/* Danger Zone */}
      <div className="bg-red-500/5 border border-red-500/20 rounded-lg p-6 shadow-xl">
        <div className="flex items-center gap-3 mb-6">
          <AlertTriangle className="h-6 w-6 text-red-500" />
          <h2 className="text-xl font-semibold text-white">Danger Zone</h2>
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-gray-900/50 rounded-lg border border-gray-800">
            <div>
              <h3 className="text-white font-medium">Clear Old Sessions</h3>
              <p className="text-sm text-gray-400 mt-1">
                Remove completed analysis sessions older than 30 days
              </p>
            </div>
            <button
              onClick={handleClearSessions}
              className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg transition-colors border border-gray-700"
            >
              Clear Sessions
            </button>
          </div>

          <div className="flex items-center justify-between p-4 bg-gray-900/50 rounded-lg border border-red-500/30">
            <div>
              <h3 className="text-red-400 font-medium">Reset Database</h3>
              <p className="text-sm text-gray-400 mt-1">
                ⚠️ Permanently delete all data. This cannot be undone.
              </p>
            </div>
            <button
              onClick={handleResetDatabase}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
            >
              Reset Database
            </button>
          </div>
        </div>
      </div>

      {/* Info Card */}
      <div className="bg-blue-500/5 border border-blue-500/20 rounded-lg p-6">
        <h3 className="text-white font-semibold mb-2">About FixIt</h3>
        <p className="text-sm text-gray-400 mb-2">
          Version 1.0.0 - Powered by Gemini 3
        </p>
        <p className="text-sm text-gray-400">
          An autonomous security agent that detects vulnerabilities, generates tests, and creates verified fixes automatically.
        </p>
      </div>
    </div>
  );
}
