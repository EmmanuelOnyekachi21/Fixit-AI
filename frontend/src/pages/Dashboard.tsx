import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Github, Play, FileCode, AlertTriangle, Shield, CheckCircle } from 'lucide-react';
import type { AnalysisStatus } from '../types';
import { StatsCard } from '../components/StatsCard';

import { getSessions, startAnalysis, isBackendAvailable } from '../api'


export default function Dashboard() {
  const navigate = useNavigate();
  const [repoUrl, setRepoUrl] = useState('');
  const [autoCreatePRs, setAutoCreatePRs] = useState(true);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  // state for data
  const [sessions, setSessions] = useState<any[]>([]);
  const [summary, setSummary] = useState<any>({});
  const [isLoading, setIsLoading] = useState(true);
  const [usingMockData, setUsingMockData] = useState(false);


  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      try {
        const data = await getSessions();
        setSessions(data.sessions);
        setSummary(data.summary);
        setUsingMockData(!isBackendAvailable());
      } catch (err: any) {
        console.error('Error fetching sessions:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [])

  const handleAnalyze = async () => {
    if (!repoUrl.trim()) return;
    
    setIsAnalyzing(true);
    
    try {
      const result = await startAnalysis(repoUrl, autoCreatePRs);
      
      // Navigate to analysis progress page with session ID
      if (result.session_id) {
        navigate(`/analysis/${result.session_id}`);
      } else {
        // Fallback to demo if no session ID
        navigate('/analysis/demo');
      }
    } catch (error: any) {
      console.error('Failed to start analysis:', error);
      alert(error.message || 'Failed to start analysis. Please check the repository URL.');
      setIsAnalyzing(false);
    }
  };

  const getStatusColor = (status: AnalysisStatus) => {
    switch (status) {
      case 'running':
        return 'bg-blue-500/10 text-blue-400 border-blue-500/20';
      case 'completed':
        return 'bg-green-500/10 text-green-400 border-green-500/20';
      case 'failed':
        return 'bg-red-500/10 text-red-400 border-red-500/20';
      case 'pending':
        return 'bg-gray-500/10 text-gray-400 border-gray-500/20';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // Calculate summary stats
  const totalFiles = summary?.total_files || 0;
  const totalVulnerabilities = summary?.total_vulnerabilities || 0;
  const totalPRs = summary?.total_prs || 0;
  const completedSessions = summary?.total_scans || 0;

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold text-white">
          Autonomous Security Analysis
        </h1>
        <p className="text-lg text-gray-400 max-w-2xl mx-auto">
          AI-powered vulnerability detection, test generation, and automated fixes
        </p>
        {usingMockData && (
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
            <div className="h-2 w-2 rounded-full bg-yellow-500"></div>
            <span className="text-sm text-yellow-400">Demo Mode - Using sample data</span>
          </div>
        )}
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard
          title="Total Scans"
          value={completedSessions}
          icon={Shield}
          iconColor="bg-blue-500/10 text-blue-500"
        />
        <StatsCard
          title="Files Analyzed"
          value={totalFiles}
          icon={FileCode}
          iconColor="bg-purple-500/10 text-purple-500"
        />
        <StatsCard
          title="Vulnerabilities Found"
          value={totalVulnerabilities}
          icon={AlertTriangle}
          iconColor="bg-orange-500/10 text-orange-500"
        />
        <StatsCard
          title="PRs Created"
          value={totalPRs}
          icon={CheckCircle}
          iconColor="bg-green-500/10 text-green-500"
        />
      </div>

      {/* Analyze Repository Card */}
      <div className="bg-gray-900 border border-gray-800 rounded-lg p-6 shadow-xl">
        <div className="flex items-center gap-3 mb-6">
          <Github className="h-6 w-6 text-blue-500" />
          <h2 className="text-xl font-semibold text-white">Analyze Repository</h2>
        </div>

        <div className="space-y-4">
          <div>
            <label htmlFor="repo-url" className="block text-sm font-medium text-gray-300 mb-2">
              GitHub Repository URL
            </label>
            <input
              id="repo-url"
              type="text"
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              placeholder="https://github.com/owner/repository"
              className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            />
          </div>

          <div className="flex items-center gap-3">
            <input
              id="auto-pr"
              type="checkbox"
              checked={autoCreatePRs}
              onChange={(e) => setAutoCreatePRs(e.target.checked)}
              className="w-4 h-4 text-blue-600 bg-gray-800 border-gray-700 rounded focus:ring-blue-500 focus:ring-2"
            />
            <label htmlFor="auto-pr" className="text-sm text-gray-300">
              Automatically create pull requests for verified fixes
            </label>
          </div>

          <button
            onClick={handleAnalyze}
            disabled={!repoUrl.trim() || isAnalyzing}
            className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition-colors"
          >
            {isAnalyzing ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                Starting Analysis...
              </>
            ) : (
              <>
                <Play className="h-5 w-5" />
                Start Analysis
              </>
            )}
          </button>
        </div>
      </div>

      {/* Recent Analysis Sessions */}
      <div className="bg-gray-900 border border-gray-800 rounded-lg shadow-xl overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-800">
          <h2 className="text-xl font-semibold text-white">Recent Analysis Sessions</h2>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-800/50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Repository
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Files
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Vulnerabilities
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  PRs Created
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Started At
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800">
              {isLoading ? (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-center">
                    <div className="flex items-center justify-center gap-3">
                      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
                      <span className="text-gray-400">Loading sessions...</span>
                    </div>
                  </td>
                </tr>
              ) : sessions.length > 0 ? (
                  sessions.map((session: any) => (
                    <tr 
                      key={session.id} 
                      onClick={() => {
                        if (session.status === 'completed') {
                          navigate('/vulnerabilities');
                        } else {
                          navigate(`/analysis/${session.session_id}`);
                        }
                      }}
                      className="hover:bg-gray-800/30 transition-colors cursor-pointer"
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10 bg-gray-700 rounded-lg flex items-center justify-center">
                            <Github className="h-6 w-6 text-blue-500" />
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-white">{session.repository_name}</div>
                            <div className="text-sm text-gray-400">{session.repository_name.split('/')[0]}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full border ${getStatusColor(session.status)}`}>
                          {session.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                        {session.files_analyzed}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                        {session.vulnerabilities_found}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                        {session.prs_created}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                        {formatDate(session.started_at)}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={6} className="px-6 py-4 text-center text-sm text-gray-500">
                      No analysis sessions found
                    </td>
                  </tr>
                )
              }
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
