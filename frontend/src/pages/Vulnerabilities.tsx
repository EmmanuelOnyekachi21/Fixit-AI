import { useState, useEffect } from 'react';
import { AlertTriangle, ExternalLink, Filter, ChevronDown, ChevronUp, Github, Calendar, FileCode, Wrench, Rocket } from 'lucide-react';
import { mockTasks } from '../data/mockData';
import type { Task, Severity, TaskStatus } from '../types';
import VulnerabilityDetailModal from '../components/VulnerabilityDetailModal';
import FixReviewModal from '../components/FixReviewModal';
import { getRepositoryTasks, generateFix, processAllTasks, getTaskDetail } from '../api';

interface RepositoryGroup {
  repository_id: number;
  repository_name: string;
  repository_url: string;
  session_id: string;
  analyzed_at: string;
  tasks: Task[];
}

export default function Vulnerabilities() {
  const [repositoryGroups, setRepositoryGroups] = useState<RepositoryGroup[]>([]);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [reviewTask, setReviewTask] = useState<Task | null>(null);
  const [severityFilter, setSeverityFilter] = useState<Severity | 'all'>('all');
  const [statusFilter, setStatusFilter] = useState<TaskStatus | 'all'>('all');
  const [expandedRepos, setExpandedRepos] = useState<Set<number>>(new Set());
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set());
  const [isLoading, setIsLoading] = useState(true);
  const [usingMockData, setUsingMockData] = useState(false);
  const [processingTasks, setProcessingTasks] = useState<Set<number>>(new Set());
  const [processingSessions, setProcessingSessions] = useState<Set<string>>(new Set());

  // Fetch tasks grouped by repository
  useEffect(() => {
    const fetchTasksByRepository = async () => {
      setIsLoading(true);
      try {
        // Get all sessions
        const sessionsResponse = await fetch('http://localhost:8000/api/v1/sessions/');
        const sessionsData = await sessionsResponse.json();
        
        console.log('📊 Sessions data:', sessionsData);
        
        if (sessionsData.sessions && sessionsData.sessions.length > 0) {
          const groups: RepositoryGroup[] = [];
          
          // Process each completed session
          for (const session of sessionsData.sessions) {
            console.log('🔍 Processing session:', session.id, 'Status:', session.status);
            
            if (session.status === 'completed') {
              try {
                // Get detailed session info to get repository_id
                const sessionDetailResponse = await fetch(`http://localhost:8000/api/v1/sessions/${session.id}/status/`);
                const sessionDetail = await sessionDetailResponse.json();
                
                console.log('📝 Session detail:', sessionDetail);
                
                if (sessionDetail.repository && sessionDetail.repository.id) {
                  const data = await getRepositoryTasks(sessionDetail.repository.id);
                  
                  console.log('📋 Tasks data:', data);
                  
                  if (data.tasks && data.tasks.length > 0) {
                    // Construct repository name from session data
                    const repoName = session.repository_name || sessionDetail.repository.name;
                    
                    groups.push({
                      repository_id: sessionDetail.repository.id,
                      repository_name: repoName,
                      repository_url: sessionDetail.repository.url,
                      session_id: sessionDetail.session_id,
                      analyzed_at: session.started_at,
                      tasks: data.tasks
                    });
                  }
                }
              } catch (error) {
                console.error(`Failed to fetch details for session ${session.id}:`, error);
              }
            }
          }
          
          console.log('✅ Final groups:', groups);
          
          if (groups.length > 0) {
            setRepositoryGroups(groups);
            setUsingMockData(false);
            // Auto-expand the first repository
            setExpandedRepos(new Set([groups[0].repository_id]));
          } else {
            // No real data, use mock data
            console.log('⚠️ No completed sessions with tasks, using mock data');
            setRepositoryGroups([{
              repository_id: 1,
              repository_name: 'example/demo-app',
              repository_url: 'https://github.com/example/demo-app',
              session_id: 'demo',
              analyzed_at: new Date().toISOString(),
              tasks: mockTasks
            }]);
            setUsingMockData(true);
            setExpandedRepos(new Set([1]));
          }
        } else {
          // No sessions, use mock data
          console.log('⚠️ No sessions found, using mock data');
          setRepositoryGroups([{
            repository_id: 1,
            repository_name: 'example/demo-app',
            repository_url: 'https://github.com/example/demo-app',
            session_id: 'demo',
            analyzed_at: new Date().toISOString(),
            tasks: mockTasks
          }]);
          setUsingMockData(true);
          setExpandedRepos(new Set([1]));
        }
      } catch (error) {
        console.error('Failed to fetch sessions:', error);
        // Fallback to mock data
        setRepositoryGroups([{
          repository_id: 1,
          repository_name: 'example/demo-app',
          repository_url: 'https://github.com/example/demo-app',
          session_id: 'demo',
          analyzed_at: new Date().toISOString(),
          tasks: mockTasks
        }]);
        setUsingMockData(true);
        setExpandedRepos(new Set([1]));
      } finally {
        setIsLoading(false);
      }
    };

    fetchTasksByRepository();
  }, []);

  // Get all tasks for filtering
  const allTasks = repositoryGroups.flatMap(group => group.tasks);
  const totalVulnerabilities = allTasks.length;

  const getSeverityColor = (severity: Severity) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-500 text-white';
      case 'high':
        return 'bg-orange-500 text-white';
      case 'medium':
        return 'bg-yellow-500 text-gray-900';
      case 'low':
        return 'bg-blue-500 text-white';
    }
  };

  const getStatusColor = (status: TaskStatus | FixStatus) => {
    switch (status) {
      case 'pr_created':
        return 'bg-green-500/10 text-green-400 border-green-500/20';
      case 'verified':
      case 'completed':
        return 'bg-blue-500/10 text-blue-400 border-blue-500/20';
      case 'generated':
        return 'bg-purple-500/10 text-purple-400 border-purple-500/20';
      case 'processing':
        return 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20';
      case 'false_positive':
        return 'bg-gray-500/10 text-gray-400 border-gray-500/20';
      case 'failed':
      case 'pr_failed':
        return 'bg-red-500/10 text-red-400 border-red-500/20';
      case 'pending':
      default:
        return 'bg-gray-500/10 text-gray-400 border-gray-500/20';
    }
  };

  // Filter tasks within each repository group
  const filteredRepositoryGroups = repositoryGroups.map(group => ({
    ...group,
    tasks: group.tasks.filter((task) => {
      if (severityFilter !== 'all' && task.severity !== severityFilter) return false;
      if (statusFilter !== 'all' && task.fix_status !== statusFilter) return false;
      return true;
    })
  })).filter(group => group.tasks.length > 0); // Only show repos with matching tasks

  const toggleRepo = (repoId: number) => {
    setExpandedRepos((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(repoId)) {
        newSet.delete(repoId);
      } else {
        newSet.add(repoId);
      }
      return newSet;
    });
  };

  const toggleRow = (id: number) => {
    setExpandedRows((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        newSet.add(id);
      }
      return newSet;
    });
  };

  // Handler for generating fix for a single task
  const handleGenerateFix = async (taskId: number, createPR: boolean) => {
    try {
      setProcessingTasks(prev => new Set(prev).add(taskId));
      
      const result = await generateFix(taskId, createPR);
      
      alert(
        `✅ Verification workflow started!\n\n` +
        `Task ID: ${taskId}\n` +
        `Celery Task: ${result.celery_task_id}\n\n` +
        `The system will:\n` +
        `1. Generate test to verify vulnerability exists\n` +
        `2. Generate fix for the vulnerability\n` +
        `3. Verify the fix works\n` +
        `${createPR ? '4. Create a PR with the verified fix\n' : ''}\n` +
        `This may take a few minutes...`
      );
      
      // Optionally refresh the task list after a delay
      setTimeout(() => {
        window.location.reload();
      }, 5000);
      
    } catch (error: any) {
      console.error('Failed to generate fix:', error);
      alert(`❌ Failed to start verification:\n${error.message}`);
    } finally {
      setProcessingTasks(prev => {
        const newSet = new Set(prev);
        newSet.delete(taskId);
        return newSet;
      });
    }
  };

  // Handler for reviewing a generated fix
  const handleReviewFix = async (taskId: number) => {
    try {
      const taskDetail = await getTaskDetail(taskId);
      setReviewTask(taskDetail);
    } catch (error: any) {
      console.error('Failed to load task details:', error);
      alert(`❌ Failed to load fix details:\n${error.message}`);
    }
  };

  // Handler for approving a fix
  const handleApproveFix = async (taskId: number, createPR: boolean) => {
    if (createPR) {
      // If user wants to create PR, trigger that
      try {
        const result = await generateFix(taskId, true);
        alert(`✅ PR creation started!\n\nTask ID: ${taskId}\nCelery Task: ${result.celery_task_id}`);
        setTimeout(() => window.location.reload(), 3000);
      } catch (error: any) {
        alert(`❌ Failed to create PR:\n${error.message}`);
      }
    } else {
      // Just mark as approved
      alert(`✅ Fix approved for Task ${taskId}`);
    }
  };

  // Handler for rejecting a fix
  const handleRejectFix = (taskId: number) => {
    alert(`❌ Fix rejected for Task ${taskId}\n\nYou can regenerate the fix or manually edit it.`);
  };

  // Handler for processing all tasks in a session
  const handleProcessAll = async (sessionId: string, createPR: boolean) => {
    const action = createPR ? 'verify and fix ALL vulnerabilities, then create PRs' : 'verify and fix ALL vulnerabilities';
    const confirmed = confirm(
      `⚠️ This will ${action} in this repository.\n\n` +
      `Each vulnerability will be:\n` +
      `• Verified with a test\n` +
      `• Fixed automatically\n` +
      `• Verified that the fix works\n` +
      `${createPR ? '• Submitted as a PR to GitHub\n' : ''}\n` +
      `This may take several minutes and will use API credits.\n\n` +
      `Continue?`
    );
    
    if (!confirmed) return;
    
    try {
      setProcessingSessions(prev => new Set(prev).add(sessionId));
      
      const result = await processAllTasks(sessionId, createPR);
      
      alert(
        `✅ Verification workflow started!\n\n` +
        `Session: ${sessionId}\n` +
        `Total Tasks: ${result.total_tasks}\n` +
        `Celery Task: ${result.celery_task_id}\n\n` +
        `Each task will be verified and fixed automatically.\n` +
        `False positives will be filtered out.\n` +
        `This will take several minutes...`
      );
      
      // Optionally refresh after a delay
      setTimeout(() => {
        window.location.reload();
      }, 8000);
      
    } catch (error: any) {
      console.error('Failed to process all tasks:', error);
      alert(`❌ Failed to start processing:\n${error.message}`);
    } finally {
      setProcessingSessions(prev => {
        const newSet = new Set(prev);
        newSet.delete(sessionId);
        return newSet;
      });
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Vulnerabilities</h1>
          <p className="text-gray-400 mt-1">
            {totalVulnerabilities} vulnerabilities found across {repositoryGroups.length} repositories
            {usingMockData && (
              <span className="ml-2 text-xs text-yellow-400">(Demo data)</span>
            )}
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-gray-900 border border-gray-800 rounded-lg p-4 shadow-xl">
        <div className="flex items-center gap-4 flex-wrap">
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-gray-400" />
            <span className="text-sm text-gray-400">Filters:</span>
          </div>

          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value as Severity | 'all')}
            className="px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Severities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as TaskStatus | 'all')}
            className="px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Statuses</option>
            <option value="pr_created">PR Created</option>
            <option value="completed">Completed</option>
            <option value="verified">Verified</option>
            <option value="processing">Processing</option>
            <option value="false_positive">False Positive</option>
            <option value="failed">Failed</option>
            <option value="pending">Pending</option>
          </select>
        </div>
      </div>

      {/* Loading State */}
      {isLoading ? (
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-8 shadow-xl">
          <div className="flex items-center justify-center gap-3">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
            <span className="text-gray-400">Loading vulnerabilities...</span>
          </div>
        </div>
      ) : filteredRepositoryGroups.length === 0 ? (
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-8 shadow-xl text-center">
          <AlertTriangle className="h-12 w-12 text-gray-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-white mb-2">No vulnerabilities found</h3>
          <p className="text-gray-400">
            {repositoryGroups.length === 0 
              ? "No repositories have been analyzed yet. Start by analyzing a repository from the dashboard."
              : "No vulnerabilities match your current filters."
            }
          </p>
        </div>
      ) : (
        /* Repository Groups */
        <div className="space-y-6">
          {filteredRepositoryGroups.map((group) => (
            <div key={group.repository_id} className="bg-gray-900 border border-gray-800 rounded-lg shadow-xl overflow-hidden">
              {/* Repository Header */}
              <div className="px-6 py-4 bg-gray-800/50 border-b border-gray-700">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-3">
                      <Github className="h-5 w-5 text-blue-500" />
                      <div>
                        <h3 className="text-lg font-semibold text-white">{group.repository_name}</h3>
                        <div className="flex items-center gap-4 text-sm text-gray-400">
                          <div className="flex items-center gap-1">
                            <Calendar className="h-4 w-4" />
                            <span>Analyzed {new Date(group.analyzed_at).toLocaleDateString()}</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <AlertTriangle className="h-4 w-4" />
                            <span>{group.tasks.length} vulnerabilities</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <a
                      href={group.repository_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded transition-colors flex items-center gap-1"
                    >
                      View Repo
                      <ExternalLink className="h-3 w-3" />
                    </a>
                    <button
                      onClick={() => toggleRepo(group.repository_id)}
                      className="text-gray-400 hover:text-white transition-colors"
                    >
                      {expandedRepos.has(group.repository_id) ? (
                        <ChevronUp className="h-5 w-5" />
                      ) : (
                        <ChevronDown className="h-5 w-5" />
                      )}
                    </button>
                  </div>
                </div>
                
                {/* Action Buttons */}
                <div className="flex items-center gap-3 pt-3 border-t border-gray-700">
                  <button
                    onClick={() => handleProcessAll(group.session_id, false)}
                    disabled={processingSessions.has(group.session_id)}
                    className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white text-sm rounded-lg transition-colors"
                  >
                    <Wrench className="h-4 w-4" />
                    {processingSessions.has(group.session_id) ? 'Processing...' : 'Verify & Fix All'}
                  </button>
                  <button
                    onClick={() => handleProcessAll(group.session_id, true)}
                    disabled={processingSessions.has(group.session_id)}
                    className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white text-sm rounded-lg transition-colors"
                  >
                    <Rocket className="h-4 w-4" />
                    {processingSessions.has(group.session_id) ? 'Processing...' : 'Verify, Fix & Create PRs'}
                  </button>
                  <span className="text-xs text-gray-400 ml-2">
                    {group.tasks.filter(t => t.fix_code).length} / {group.tasks.length} fixes generated
                  </span>
                </div>
              </div>

              {/* Vulnerabilities Table */}
              {expandedRepos.has(group.repository_id) && (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-800/30">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                          Severity
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                          Type
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                          File & Line
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                          Status
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                          Actions
                        </th>
                        <th className="px-6 py-3"></th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-800">
                      {group.tasks.map((task) => (
                        <>
                          <tr
                            key={task.id}
                            className="hover:bg-gray-800/30 transition-colors"
                          >
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span
                                className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold uppercase ${getSeverityColor(
                                  task.severity
                                )}`}
                              >
                                {task.severity}
                              </span>
                            </td>
                            <td className="px-6 py-4">
                              <div className="flex items-center gap-2">
                                <AlertTriangle className="h-4 w-4 text-orange-500" />
                                <span className="text-sm font-medium text-white">
                                  {task.vulnerability_type}
                                </span>
                              </div>
                            </td>
                            <td className="px-6 py-4">
                              <div className="text-sm">
                                <div className="text-white font-mono">{task.file_path}</div>
                                <div className="text-gray-400">Line {task.line_number}</div>
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span
                                className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getStatusColor(
                                  task.fix_status
                                )}`}
                              >
                                {task.fix_status.replace('_', ' ')}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="flex items-center gap-2 flex-wrap">
                                <button
                                  onClick={() => setSelectedTask(task)}
                                  className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded transition-colors"
                                >
                                  View Details
                                </button>
                                
                                {/* Generate Fix Button (if no fix yet) */}
                                {!task.fix_code && (
                                  <>
                                    <button
                                      onClick={() => handleGenerateFix(task.id, false)}
                                      disabled={processingTasks.has(task.id)}
                                      className="px-3 py-1 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white text-sm rounded transition-colors flex items-center gap-1"
                                    >
                                      <Wrench className="h-3 w-3" />
                                      {processingTasks.has(task.id) ? 'Verifying...' : 'Verify & Fix'}
                                    </button>
                                    <button
                                      onClick={() => handleGenerateFix(task.id, true)}
                                      disabled={processingTasks.has(task.id)}
                                      className="px-3 py-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white text-sm rounded transition-colors flex items-center gap-1"
                                    >
                                      <Rocket className="h-3 w-3" />
                                      {processingTasks.has(task.id) ? 'Verifying...' : 'Verify, Fix & PR'}
                                    </button>
                                  </>
                                )}
                                
                                {/* Review Fix Button (if fix generated but no PR yet) */}
                                {task.fix_code && !task.pr_url && (
                                  <button
                                    onClick={() => handleReviewFix(task.id)}
                                    className="px-3 py-1 bg-yellow-600 hover:bg-yellow-700 text-white text-sm rounded transition-colors flex items-center gap-1"
                                  >
                                    <AlertTriangle className="h-3 w-3" />
                                    Review Fix
                                  </button>
                                )}
                                
                                {/* Status Indicators */}
                                {task.fix_code && (
                                  <span className="text-xs text-green-400 flex items-center gap-1">
                                    ✓ Fix Generated
                                  </span>
                                )}
                                {task.test_code && (
                                  <span className="text-xs text-blue-400 flex items-center gap-1">
                                    ✓ Tests
                                  </span>
                                )}
                                
                                {task.pr_url && (
                                  <a
                                    href={task.pr_url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="px-3 py-1 bg-green-600 hover:bg-green-700 text-white text-sm rounded transition-colors flex items-center gap-1"
                                  >
                                    View PR
                                    <ExternalLink className="h-3 w-3" />
                                  </a>
                                )}
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-right">
                              <button
                                onClick={() => toggleRow(task.id)}
                                className="text-gray-400 hover:text-white transition-colors"
                              >
                                {expandedRows.has(task.id) ? (
                                  <ChevronUp className="h-5 w-5" />
                                ) : (
                                  <ChevronDown className="h-5 w-5" />
                                )}
                              </button>
                            </td>
                          </tr>
                          {expandedRows.has(task.id) && (
                            <tr key={`${task.id}-expanded`}>
                              <td colSpan={6} className="px-6 py-4 bg-gray-800/20">
                                <div className="space-y-3">
                                  <div>
                                    <h4 className="text-sm font-semibold text-white mb-1">Description</h4>
                                    <p className="text-sm text-gray-300">{task.description}</p>
                                  </div>
                                  <div className="grid grid-cols-2 gap-4">
                                    <div>
                                      <h4 className="text-sm font-semibold text-white mb-2">Original Code</h4>
                                      <pre className="bg-gray-900 border border-gray-700 rounded p-3 text-xs text-gray-300 overflow-x-auto">
                                        <code>{task.original_code}</code>
                                      </pre>
                                    </div>
                                    <div>
                                      <h4 className="text-sm font-semibold text-white mb-2">Fixed Code</h4>
                                      <pre className="bg-gray-900 border border-green-700/50 rounded p-3 text-xs text-gray-300 overflow-x-auto">
                                        <code>{task.fix_code}</code>
                                      </pre>
                                    </div>
                                  </div>
                                </div>
                              </td>
                            </tr>
                          )}
                        </>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Modals */}
      {selectedTask && (
        <VulnerabilityDetailModal
          task={selectedTask}
          onClose={() => setSelectedTask(null)}
        />
      )}
      
      {reviewTask && (
        <FixReviewModal
          task={reviewTask}
          onClose={() => setReviewTask(null)}
          onApprove={handleApproveFix}
          onReject={handleRejectFix}
        />
      )}
    </div>
  );
}
