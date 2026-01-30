import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Github, Play, Clock, FileCode, AlertTriangle, GitPullRequest, Shield, CheckCircle } from 'lucide-react';
import { mockRepositories } from '../data/mockData';
import type { AnalysisStatus } from '../types';
import { StatsCard } from '../components/StatsCard';

export default function Dashboard() {
  const navigate = useNavigate();
  const [repoUrl, setRepoUrl] = useState('');
  const [autoCreatePRs, setAutoCreatePRs] = useState(true);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleAnalyze = () => {
    if (!repoUrl.trim()) return;
    
    setIsAnalyzing(true);
    setTimeout(() => {
      navigate('/analysis/demo');
    }, 500);
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
  const totalFiles = mockRepositories.reduce((sum, repo) => sum + repo.files_analyzed, 0);
  const totalVulnerabilities = mockRepositories.reduce((sum, repo) => sum + repo.vulnerabilities_found, 0);
  const totalPRs = mockRepositories.reduce((sum, repo) => sum + repo.prs_created, 0);
  const completedSessions = mockRepositories.filter(r => r.status === 'completed').length;

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
              {mockRepositories.map((repo) => (
                <tr
                  key={repo.id}
                  onClick={() => navigate(`/analysis/${repo.id}`)}
                  className="hover:bg-gray-800/50 cursor-pointer transition-colors"
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      <Github className="h-4 w-4 text-gray-500" />
                      <span className="text-sm font-medium text-white">{repo.name}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getStatusColor(
                        repo.status
                      )} ${repo.status === 'running' ? 'animate-pulse' : ''}`}
                    >
                      {repo.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-1 text-sm text-gray-300">
                      <FileCode className="h-4 w-4 text-gray-500" />
                      {repo.files_analyzed}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-1 text-sm text-gray-300">
                      <AlertTriangle className="h-4 w-4 text-orange-500" />
                      {repo.vulnerabilities_found}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-1 text-sm text-gray-300">
                      <GitPullRequest className="h-4 w-4 text-green-500" />
                      {repo.prs_created}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-1 text-sm text-gray-400">
                      <Clock className="h-4 w-4" />
                      {formatDate(repo.started_at)}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
