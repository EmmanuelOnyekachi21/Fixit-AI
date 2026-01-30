import { useState } from 'react';
import { AlertTriangle, ExternalLink, Filter, ChevronDown, ChevronUp } from 'lucide-react';
import { mockTasks } from '../data/mockData';
import type { Task, Severity, TaskStatus } from '../types';
import VulnerabilityDetailModal from '../components/VulnerabilityDetailModal';

export default function Vulnerabilities() {
  const [tasks] = useState<Task[]>(mockTasks);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [severityFilter, setSeverityFilter] = useState<Severity | 'all'>('all');
  const [statusFilter, setStatusFilter] = useState<TaskStatus | 'all'>('all');
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set());

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

  const getStatusColor = (status: TaskStatus) => {
    switch (status) {
      case 'pr_created':
        return 'bg-green-500/10 text-green-400 border-green-500/20';
      case 'verified':
        return 'bg-blue-500/10 text-blue-400 border-blue-500/20';
      case 'test_generated':
        return 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20';
      case 'detected':
        return 'bg-gray-500/10 text-gray-400 border-gray-500/20';
    }
  };

  const filteredTasks = tasks.filter((task) => {
    if (severityFilter !== 'all' && task.severity !== severityFilter) return false;
    if (statusFilter !== 'all' && task.fix_status !== statusFilter) return false;
    return true;
  });

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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Vulnerabilities</h1>
          <p className="text-gray-400 mt-1">
            {filteredTasks.length} vulnerabilities found
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
            <option value="verified">Verified</option>
            <option value="test_generated">Test Generated</option>
            <option value="detected">Detected</option>
          </select>
        </div>
      </div>

      {/* Vulnerabilities Table */}
      <div className="bg-gray-900 border border-gray-800 rounded-lg shadow-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-800/50">
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
              {filteredTasks.map((task) => (
                <>
                  <tr
                    key={task.id}
                    className="hover:bg-gray-800/50 transition-colors"
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
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => setSelectedTask(task)}
                          className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded transition-colors"
                        >
                          View Details
                        </button>
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
                      <td colSpan={6} className="px-6 py-4 bg-gray-800/30">
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
      </div>

      {/* Modal */}
      {selectedTask && (
        <VulnerabilityDetailModal
          task={selectedTask}
          onClose={() => setSelectedTask(null)}
        />
      )}
    </div>
  );
}
