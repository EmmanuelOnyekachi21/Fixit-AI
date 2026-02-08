import { useState, useEffect } from 'react';
import { Github, CheckCircle, XCircle, AlertTriangle, Save, Zap, Loader } from 'lucide-react';
import { validateCredentials } from '../api';

export default function Settings() {
  const [mode, setMode] = useState<'demo' | 'real' | null>(null);
  const [geminiKey, setGeminiKey] = useState('');
  const [githubToken, setGithubToken] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [username, setUsername] = useState('');
  const [isTesting, setIsTesting] = useState(false);
  const [maxFiles, setMaxFiles] = useState(100);
  const [autoCreatePRs, setAutoCreatePRs] = useState(true);
  const [checkpointInterval, setCheckpointInterval] = useState(10);
  const [saved, setSaved] = useState(false);
  
  // Validation state
  const [isValidating, setIsValidating] = useState(false);
  const [validationStatus, setValidationStatus] = useState<'idle' | 'valid' | 'invalid'>('idle');
  const [validationMessage, setValidationMessage] = useState('');

  useEffect(() => {
    const savedMode = localStorage.getItem('fixit_mode') as 'demo' | 'real' | null;
    setMode(savedMode);
    
    // Load saved credentials if they exist
    const savedGeminiKey = localStorage.getItem('gemini_key');
    const savedGithubToken = localStorage.getItem('github_token');
    if (savedGeminiKey) setGeminiKey(savedGeminiKey);
    if (savedGithubToken) setGithubToken(savedGithubToken);
    
    // If both exist, mark as valid
    if (savedGeminiKey && savedGithubToken) {
      setValidationStatus('valid');
      setValidationMessage('✓ Credentials loaded from previous session');
    }
  }, []);

  const handleValidateCredentials = async () => {
    if (!geminiKey.trim() || !githubToken.trim()) {
      setValidationStatus('invalid');
      setValidationMessage('✗ Please enter both API keys');
      return;
    }

    setIsValidating(true);
    setValidationStatus('idle');
    
    try {
      const result = await validateCredentials(geminiKey, githubToken);
      
      if (result.valid) {
        setValidationStatus('valid');
        setValidationMessage('✓ Credentials validated successfully!');
        // Store in localStorage
        localStorage.setItem('gemini_key', geminiKey);
        localStorage.setItem('github_token', githubToken);
      } else {
        setValidationStatus('invalid');
        setValidationMessage(`✗ ${result.error || 'Invalid credentials'}`);
      }
    } catch (error: any) {
      setValidationStatus('invalid');
      setValidationMessage(`✗ ${error.message || 'Failed to validate credentials'}`);
    } finally {
      setIsValidating(false);
    }
  };

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
    if (mode === 'real' && (!geminiKey.trim() || !githubToken.trim())) {
      alert('Please provide both Gemini API key and GitHub token for real-time mode');
      return;
    }
    
    // Save to localStorage
    if (geminiKey) localStorage.setItem('gemini_api_key', geminiKey);
    if (githubToken) localStorage.setItem('github_token', githubToken);
    
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

      {/* Real-Time Mode Setup Banner */}
      {mode === 'real' && (
        <div className="bg-gradient-to-r from-purple-600/20 to-pink-600/20 border border-purple-500/50 rounded-lg p-6 flex items-start gap-4">
          <div className="flex-shrink-0">
            <Zap className="h-6 w-6 text-purple-400 mt-1" />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-purple-300 mb-2">🚀 Complete Your Setup</h3>
            <p className="text-gray-300 mb-4">
              You're in Real-Time Mode! To get started, you need to provide your API keys below. This is a one-time setup.
            </p>
            <div className="space-y-2 text-sm text-gray-400">
              <p>✓ Get your <span className="text-blue-400 font-semibold">Gemini API Key</span> from: <a href="https://aistudio.google.com/app/apikey" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline">aistudio.google.com/app/apikey</a></p>
              <p>✓ Get your <span className="text-blue-400 font-semibold">GitHub Token</span> from: <a href="https://github.com/settings/tokens" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline">github.com/settings/tokens</a></p>
              <p className="text-xs text-gray-500 mt-3">GitHub token needs: <code className="bg-gray-800 px-2 py-1 rounded">repo</code> and <code className="bg-gray-800 px-2 py-1 rounded">workflow</code> scopes</p>
            </div>
          </div>
        </div>
      )}

      {/* API Keys Section */}
      <div className="bg-gray-900 border border-gray-800 rounded-lg p-6 shadow-xl">
        <h2 className="text-xl font-semibold text-white mb-6">API Keys</h2>

        <div className="space-y-4">
          {/* Gemini API Key */}
          <div>
            <label htmlFor="gemini-key" className="block text-sm font-medium text-gray-300 mb-2">
              Gemini API Key
            </label>
            <input
              id="gemini-key"
              type="password"
              value={geminiKey}
              onChange={(e) => setGeminiKey(e.target.value)}
              placeholder="AIzaSy..."
              className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
            />
            <p className="text-xs text-gray-500 mt-2">
              Get your key at: <span className="text-blue-400">aistudio.google.com/app/apikey</span>
            </p>
          </div>

          {/* GitHub Token */}
          <div>
            <label htmlFor="github-token" className="block text-sm font-medium text-gray-300 mb-2">
              GitHub Personal Access Token
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
              Get your token at: <span className="text-blue-400">github.com/settings/tokens</span> (requires: repo, workflow)
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={handleValidateCredentials}
              disabled={isValidating || !geminiKey.trim() || !githubToken.trim()}
              className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
            >
              {isValidating ? (
                <>
                  <Loader className="h-4 w-4 animate-spin" />
                  Validating...
                </>
              ) : (
                <>
                  <CheckCircle className="h-4 w-4" />
                  Validate Credentials
                </>
              )}
            </button>

            {validationStatus === 'valid' && (
              <div className="flex items-center gap-2 text-green-400">
                <CheckCircle className="h-5 w-5" />
                <span className="text-sm">{validationMessage}</span>
              </div>
            )}

            {validationStatus === 'invalid' && (
              <div className="flex items-center gap-2 text-red-400">
                <XCircle className="h-5 w-5" />
                <span className="text-sm">{validationMessage}</span>
              </div>
            )}
          </div>
          
          {validationStatus === 'valid' && (
            <div className="p-4 bg-green-500/10 border border-green-500/30 rounded-lg">
              <p className="text-sm text-green-300">
                ✓ Your credentials have been validated and saved. You can now analyze real repositories!
              </p>
            </div>
          )}
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

          {mode === 'real' && validationStatus === 'valid' && (
            <button
              onClick={() => {
                window.location.href = '/';
              }}
              className="flex items-center gap-2 px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-lg transition-colors w-full justify-center"
            >
              <Zap className="h-5 w-5" />
              Continue to Dashboard
            </button>
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
