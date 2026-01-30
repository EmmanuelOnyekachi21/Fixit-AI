import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Pause, X, FileCode, AlertTriangle, CheckCircle, GitPullRequest, Clock } from 'lucide-react';
import type { AnalysisSession, LogEntry } from '../types';
import { createMockSession, generateMockLog } from '../data/mockData';

export default function AnalysisProgress() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [session, setSession] = useState<AnalysisSession>(createMockSession(Number(id) || 1));
  const [isPaused, setIsPaused] = useState(false);

  useEffect(() => {
    if (isPaused || session.status !== 'running') return;

    const interval = setInterval(() => {
      setSession((prev) => {
        if (prev.files_analyzed >= prev.total_files) {
          return { ...prev, status: 'completed', progress_percentage: 100 };
        }

        const newFilesAnalyzed = prev.files_analyzed + 1;
        const newProgress = Math.round((newFilesAnalyzed / prev.total_files) * 100);
        const newVulnerabilities = Math.random() > 0.7 ? prev.vulnerabilities_found + 1 : prev.vulnerabilities_found;
        const newLog = generateMockLog(newFilesAnalyzed, prev.total_files);

        return {
          ...prev,
          files_analyzed: newFilesAnalyzed,
          progress_percentage: newProgress,
          vulnerabilities_found: newVulnerabilities,
          estimated_time_remaining: Math.max(0, prev.estimated_time_remaining - 2),
          current_file: `app/module_${newFilesAnalyzed}/views.py`,
          logs: [newLog, ...prev.logs].slice(0, 50),
        };
      });
    }, 2000);

    return () => clearInterval(interval);
  }, [isPaused, session.status]);

  const handleCancel = () => {
    setSession((prev) => ({ ...prev, status: 'failed' }));
    setTimeout(() => navigate('/'), 1000);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Analysis in Progress</h1>
          <p className="text-gray-400 mt-1">Repository: django/django</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => setIsPaused(!isPaused)}
            disabled={session.status !== 'running'}
            className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 disabled:bg-gray-900 disabled:cursor-not-allowed text-white rounded-lg transition-colors border border-gray-700"
          >
            <Pause className="h-4 w-4" />
            {isPaused ? 'Resume' : 'Pause'}
          </button>
          <button
            onClick={handleCancel}
            disabled={session.status !== 'running'}
            className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-900 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
          >
            <X className="h-4 w-4" />
            Cancel
          </button>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="bg-gray-900 border border-gray-800 rounded-lg p-6 shadow-xl">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-white">
              Analyzing: {session.files_analyzed}/{session.total_files} files ({session.progress_percentage}%)
            </h2>
            <div className="flex items-center gap-2 text-gray-400">
              <Clock className="h-4 w-4" />
              <span className="text-sm">~{formatTime(session.estimated_time_remaining)} remaining</span>
            </div>
          </div>

          <div className="relative w-full h-4 bg-gray-800 rounded-full overflow-hidden">
            <div
              className="absolute top-0 left-0 h-full bg-gradient-to-r from-blue-600 to-blue-500 transition-all duration-500 ease-out"
              style={{ width: `${session.progress_percentage}%` }}
            >
              <div className="absolute inset-0 bg-white/20 animate-pulse"></div>
            </div>
          </div>

          {session.current_file && (
            <p className="text-sm text-gray-400">
              Current file: <span className="text-blue-400 font-mono">{session.current_file}</span>
            </p>
          )}
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-6 shadow-xl">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-blue-500/10 rounded-lg">
              <FileCode className="h-6 w-6 text-blue-500" />
            </div>
            <div>
              <p className="text-sm text-gray-400">Files Analyzed</p>
              <p className="text-2xl font-bold text-white">{session.files_analyzed}</p>
            </div>
          </div>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-lg p-6 shadow-xl">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-orange-500/10 rounded-lg">
              <AlertTriangle className="h-6 w-6 text-orange-500" />
            </div>
            <div>
              <p className="text-sm text-gray-400">Vulnerabilities</p>
              <p className="text-2xl font-bold text-white">{session.vulnerabilities_found}</p>
            </div>
          </div>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-lg p-6 shadow-xl">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-green-500/10 rounded-lg">
              <CheckCircle className="h-6 w-6 text-green-500" />
            </div>
            <div>
              <p className="text-sm text-gray-400">Tests Passed</p>
              <p className="text-2xl font-bold text-white">{Math.floor(session.vulnerabilities_found * 0.8)}</p>
            </div>
          </div>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-lg p-6 shadow-xl">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-purple-500/10 rounded-lg">
              <GitPullRequest className="h-6 w-6 text-purple-500" />
            </div>
            <div>
              <p className="text-sm text-gray-400">PRs Created</p>
              <p className="text-2xl font-bold text-white">{Math.floor(session.vulnerabilities_found * 0.6)}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Live Log Feed */}
      <div className="bg-gray-900 border border-gray-800 rounded-lg shadow-xl overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-800">
          <h2 className="text-xl font-semibold text-white">Live Activity Log</h2>
        </div>
        <div className="p-4 h-96 overflow-y-auto scrollbar-thin space-y-2">
          {session.logs.length === 0 ? (
            <p className="text-gray-500 text-center py-8">Waiting for analysis to start...</p>
          ) : (
            session.logs.map((log) => (
              <div
                key={log.id}
                className="flex items-start gap-3 p-3 bg-gray-800/50 rounded-lg animate-slide-up"
              >
                <span className="text-xs text-gray-500 font-mono whitespace-nowrap">
                  {new Date(log.timestamp).toLocaleTimeString()}
                </span>
                <span className={`text-sm font-mono ${
                  log.type === 'success' ? 'text-green-400' : 
                  log.type === 'error' ? 'text-red-400' : 
                  'text-gray-300'
                }`}>
                  {log.message}
                </span>
              </div>
            ))
          )}
        </div>
      </div>

      {session.status === 'completed' && (
        <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-6 text-center">
          <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-3" />
          <h3 className="text-xl font-semibold text-white mb-2">Analysis Complete!</h3>
          <p className="text-gray-400 mb-4">
            Found {session.vulnerabilities_found} vulnerabilities across {session.files_analyzed} files
          </p>
          <button
            onClick={() => navigate('/vulnerabilities')}
            className="px-6 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
          >
            View Results
          </button>
        </div>
      )}
    </div>
  );
}
