import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Pause, X, FileCode, AlertTriangle, CheckCircle, GitPullRequest, Clock, Wifi, WifiOff, ArrowLeft } from 'lucide-react';
import type { AnalysisSession, LogEntry } from '../types';
import { createMockSession, generateMockLog } from '../data/mockData';
import { getSessionStatus } from '../api';
import { useWebSocket } from '../hooks/useWebSocket';

export default function AnalysisProgress() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [session, setSession] = useState<AnalysisSession | null>(null);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isPaused, setIsPaused] = useState(false);
  const [usingWebSocket, setUsingWebSocket] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // WebSocket connection for real-time updates
  const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000';
  const wsUrl = id && id !== 'demo'
    ? `${WS_BASE_URL}/ws/sessions/${id}/`
    : null;

  const { isConnected } = useWebSocket(wsUrl, {
    onConnect: () => {
      console.log('✅ WebSocket connected - Real-time updates enabled');
      setUsingWebSocket(true);
    },
    onDisconnect: () => {
      console.log('❌ WebSocket disconnected - Falling back to polling');
      setUsingWebSocket(false);
    },
    onMessage: (message) => {
      console.log('WebSocket message:', message);

      switch (message.type) {
        case 'session_status':
          // Initial status when connecting
          updateSessionFromData(message.data);
          break;

        case 'session_update':
          // Progress update
          setSession((prev) => {
            if (!prev) return prev;
            return {
              ...prev,
              files_analyzed: message.data.files_analyzed || prev.files_analyzed,
              total_files: message.data.total_files || prev.total_files,
              progress_percentage: message.data.progress_percentage || prev.progress_percentage,
              vulnerabilities_found: message.data.vulnerabilities_found || prev.vulnerabilities_found,
              tests_created: message.data.tests_created || prev.tests_created || 0,
              fixes_generated: message.data.fixes_generated || prev.fixes_generated || 0,
              prs_created: message.data.prs_created || prev.prs_created || 0,
              current_file: message.data.current_file || prev.current_file,
              estimated_time_remaining: message.data.estimated_time_remaining_seconds !== null && message.data.estimated_time_remaining_seconds !== undefined 
                ? message.data.estimated_time_remaining_seconds 
                : prev.estimated_time_remaining,
            };
          });
          break;

        case 'new_log':
          // New log entry - add to top of list
          setLogs((prev) => [message.data, ...prev].slice(0, 100));
          break;

        case 'analysis_complete':
          // Analysis finished
          setSession((prev) => {
            if (!prev) return prev;
            return {
              ...prev,
              status: 'completed',
              progress_percentage: 100,
              vulnerabilities_found: message.data.vulnerabilities_found || prev.vulnerabilities_found,
            };
          });
          // Auto-redirect to vulnerabilities page after 2 seconds
          setTimeout(() => {
            navigate('/vulnerabilities');
          }, 2000);
          break;

        case 'error':
          console.error('WebSocket error:', (message as any).message);
          if ((message as any).message === 'Session not found') {
            alert('Session not found. Redirecting to dashboard.');
            navigate('/');
          }
          break;
      }
    },
  });

  const updateSessionFromData = (data: any) => {
    console.log('📊 Updating session from data:', data);
    
    if (!data || !data.repository) {
      console.error('❌ Invalid session data received:', data);
      setIsLoading(false);
      return;
    }
    
    const estimatedTime = data.estimated_time_remaining_seconds;
    
    setSession({
      session_id: data.session_id,
      repository_id: data.repository.id,
      status: data.status,
      total_files: data.progress.total_files,
      files_analyzed: data.progress.files_analyzed,
      vulnerabilities_found: data.results.vulnerabilities_found,
      tests_created: data.results.tests_created || 0,
      fixes_generated: data.results.fixes_generated || 0,
      prs_created: data.results.prs_created || 0,
      progress_percentage: data.progress.percentage,
      estimated_time_remaining: estimatedTime !== null && estimatedTime !== undefined ? estimatedTime : 0,
      current_file: data.current_file || '',
      logs: [],
    });

    if (data.logs) {
      setLogs(data.logs);
    }
    
    setIsLoading(false);
    console.log('✅ Session updated successfully');
  };

  // Initialize session data on mount or when id changes
  useEffect(() => {
    if (!id) {
      navigate('/');
      return;
    }

    // Reset state when session ID changes
    setIsLoading(true);
    setLogs([]);
    setUsingWebSocket(false);
    
    // For demo mode, create mock session
    if (id === 'demo') {
      setSession(createMockSession(1));
      setIsLoading(false);
      return;
    }

    // For real sessions, fetch initial data immediately
    const fetchInitialData = async () => {
      try {
        const data = await getSessionStatus(id);
        updateSessionFromData(data);
      } catch (error) {
        console.error('Failed to fetch initial session data:', error);
        setIsLoading(false);
      }
    };

    fetchInitialData();
  }, [id, navigate]);

  // Fallback: HTTP polling when WebSocket unavailable
  useEffect(() => {
    if (!id || id === 'demo' || isLoading) return;

    const fetchStatus = async () => {
      try {
        const data = await getSessionStatus(id);
        updateSessionFromData(data);
      } catch (error) {
        console.error('Failed to fetch session status:', error);
        setIsLoading(false);
      }
    };

    // Only poll if WebSocket is not connected
    if (!usingWebSocket) {
      fetchStatus();
      const interval = setInterval(fetchStatus, 3000);
      return () => clearInterval(interval);
    }
  }, [id, usingWebSocket, isLoading]);

  // Fallback to mock simulation for demo mode ONLY
  useEffect(() => {
    if (id !== 'demo' || isPaused || !session || session.status !== 'running') return;

    const interval = setInterval(() => {
      setSession((prev) => {
        if (!prev) return prev;
        
        // Increment by 3 files per interval to speed up demo (1.5 minutes total)
        const filesPerInterval = 3;
        const newFilesAnalyzed = Math.min(prev.files_analyzed + filesPerInterval, prev.total_files);
        
        // Calculate estimated time remaining based on remaining files
        const remainingFiles = prev.total_files - newFilesAnalyzed;
        const estimatedTimePerFile = 0.6; // 600ms per file
        const newEstimatedTime = Math.max(0, remainingFiles * estimatedTimePerFile);
        
        // Check if analysis is complete
        if (newFilesAnalyzed >= prev.total_files) {
          const completedSession = { 
            ...prev, 
            status: 'completed' as const, 
            progress_percentage: 100, 
            files_analyzed: prev.total_files,
            estimated_time_remaining: 0
          };
          
          // Trigger redirect after a short delay
          setTimeout(() => {
            navigate('/vulnerabilities');
          }, 1500);
          
          return completedSession;
        }

        const newProgress = Math.round((newFilesAnalyzed / prev.total_files) * 100);
        const newVulnerabilities = Math.random() > 0.7 ? prev.vulnerabilities_found + 1 : prev.vulnerabilities_found;
        
        // Generate multiple logs for faster progression
        const newLogs: LogEntry[] = [];
        for (let i = 0; i < filesPerInterval; i++) {
          newLogs.push(generateMockLog(prev.files_analyzed + i + 1, prev.total_files));
        }

        // Add logs to logs state
        setLogs((prevLogs) => [...newLogs, ...prevLogs].slice(0, 50));

        return {
          ...prev,
          files_analyzed: newFilesAnalyzed,
          progress_percentage: newProgress,
          vulnerabilities_found: newVulnerabilities,
          estimated_time_remaining: newEstimatedTime,
          current_file: `app/module_${newFilesAnalyzed}/views.py`,
          logs: [...newLogs, ...prev.logs].slice(0, 50),
        };
      });
    }, 600); // 600ms interval instead of 2000ms

    return () => clearInterval(interval);
  }, [isPaused, session?.status, id, navigate]);

  const handleCancel = () => {
    if (session) {
      setSession({ ...session, status: 'failed' });
    }
    setTimeout(() => navigate('/'), 1000);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  // Show loading state while fetching session data
  if (isLoading || !session) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-400">Loading session...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Analysis in Progress</h1>
          <p className="text-gray-400 mt-1">
            Repository: {session.repository_id ? `Repository #${session.repository_id}` : 'django/django'}
          </p>
          <div className="flex items-center gap-3 mt-2">
            {id !== 'demo' && (
              <div className="flex items-center gap-2 text-sm">
                {isConnected ? (
                  <>
                    <Wifi className="h-4 w-4 text-green-500" />
                    <span className="text-green-400">Real-time updates</span>
                  </>
                ) : (
                  <>
                    <WifiOff className="h-4 w-4 text-yellow-500" />
                    <span className="text-yellow-400">Polling mode</span>
                  </>
                )}
              </div>
            )}
            {id === 'demo' && (
              <span className="inline-flex items-center gap-1 text-xs text-yellow-400">
                <div className="h-1.5 w-1.5 rounded-full bg-yellow-500"></div>
                Demo Mode
              </span>
            )}
          </div>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
            title="Analysis will continue running in the background"
          >
            <ArrowLeft className="h-4 w-4" />
            Run in Background
          </button>
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
              <p className="text-sm text-gray-400">Tests Created</p>
              <p className="text-2xl font-bold text-white">{session.tests_created || 0}</p>
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
              <p className="text-2xl font-bold text-white">{session.prs_created || 0}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Live Log Feed */}
      <div className="bg-gray-900 border border-gray-800 rounded-lg shadow-xl overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-800 flex items-center justify-between">
          <h2 className="text-xl font-semibold text-white">Live Activity Log</h2>
          {isConnected && (
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse"></div>
              <span className="text-xs text-green-400">Live</span>
            </div>
          )}
        </div>
        <div className="p-4 h-96 overflow-y-auto scrollbar-thin space-y-2">
          {logs.length === 0 ? (
            <p className="text-gray-500 text-center py-8">Waiting for analysis to start...</p>
          ) : (
            logs.map((log) => (
              <div
                key={log.id}
                className="flex items-start gap-3 p-3 bg-gray-800/50 rounded-lg animate-slide-up"
              >
                <span className="text-xs text-gray-500 font-mono whitespace-nowrap">
                  {new Date(log.timestamp).toLocaleTimeString()}
                </span>
                <span className={`text-sm font-mono ${log.type === 'success' ? 'text-green-400' :
                    log.type === 'error' ? 'text-red-400' :
                      log.type === 'warning' ? 'text-yellow-400' :
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
