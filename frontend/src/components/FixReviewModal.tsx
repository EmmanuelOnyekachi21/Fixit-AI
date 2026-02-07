import { useState } from 'react';
import { X, Check, AlertTriangle, Code, TestTube, GitPullRequest, Copy, CheckCircle } from 'lucide-react';
import type { Task } from '../types';

interface FixReviewModalProps {
  task: Task;
  onClose: () => void;
  onApprove: (taskId: number, createPR: boolean) => void;
  onReject: (taskId: number) => void;
}

export default function FixReviewModal({ task, onClose, onApprove, onReject }: FixReviewModalProps) {
  const [createPR, setCreatePR] = useState(true);
  const [showDiff, setShowDiff] = useState(true);
  const [copiedOriginal, setCopiedOriginal] = useState(false);
  const [copiedFix, setCopiedFix] = useState(false);

  const handleCopy = (text: string, type: 'original' | 'fix') => {
    navigator.clipboard.writeText(text);
    if (type === 'original') {
      setCopiedOriginal(true);
      setTimeout(() => setCopiedOriginal(false), 2000);
    } else {
      setCopiedFix(true);
      setTimeout(() => setCopiedFix(false), 2000);
    }
  };

  const handleApprove = () => {
    onApprove(task.id, createPR);
    onClose();
  };

  const handleReject = () => {
    onReject(task.id);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 border border-gray-800 rounded-lg shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-800 flex items-center justify-between bg-gray-800/50">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-500/10 rounded-lg">
              <Code className="h-6 w-6 text-blue-500" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Review Generated Fix</h2>
              <p className="text-sm text-gray-400">{task.title}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
          >
            <X className="h-5 w-5 text-gray-400" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Vulnerability Info */}
          <div className="bg-gray-800/30 border border-gray-700 rounded-lg p-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <span className="text-sm text-gray-400">Vulnerability Type</span>
                <p className="text-white font-medium">{task.vulnerability_type}</p>
              </div>
              <div>
                <span className="text-sm text-gray-400">Severity</span>
                <p className="text-white font-medium capitalize">{task.severity}</p>
              </div>
              <div>
                <span className="text-sm text-gray-400">File</span>
                <p className="text-white font-mono text-sm">{task.file_path}</p>
              </div>
              <div>
                <span className="text-sm text-gray-400">Line</span>
                <p className="text-white font-medium">{task.line_number}</p>
              </div>
            </div>
            <div className="mt-4">
              <span className="text-sm text-gray-400">Description</span>
              <p className="text-white mt-1">{task.description}</p>
            </div>
          </div>

          {/* View Toggle */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowDiff(true)}
              className={`px-4 py-2 rounded-lg transition-colors ${
                showDiff
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }`}
            >
              Side-by-Side Comparison
            </button>
            <button
              onClick={() => setShowDiff(false)}
              className={`px-4 py-2 rounded-lg transition-colors ${
                !showDiff
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }`}
            >
              Full Code View
            </button>
          </div>

          {/* Code Comparison */}
          {showDiff ? (
            <div className="grid grid-cols-2 gap-4">
              {/* Original Code */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4 text-red-500" />
                    <h3 className="text-sm font-semibold text-white">Original Code (Vulnerable)</h3>
                  </div>
                  <button
                    onClick={() => handleCopy(task.original_code, 'original')}
                    className="p-1 hover:bg-gray-800 rounded transition-colors"
                    title="Copy to clipboard"
                  >
                    {copiedOriginal ? (
                      <CheckCircle className="h-4 w-4 text-green-500" />
                    ) : (
                      <Copy className="h-4 w-4 text-gray-400" />
                    )}
                  </button>
                </div>
                <pre className="bg-gray-900 border border-red-700/50 rounded-lg p-4 text-xs text-gray-300 overflow-x-auto max-h-96">
                  <code>{task.original_code}</code>
                </pre>
              </div>

              {/* Fixed Code */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Check className="h-4 w-4 text-green-500" />
                    <h3 className="text-sm font-semibold text-white">Fixed Code (Secure)</h3>
                  </div>
                  <button
                    onClick={() => handleCopy(task.fix_code || '', 'fix')}
                    className="p-1 hover:bg-gray-800 rounded transition-colors"
                    title="Copy to clipboard"
                  >
                    {copiedFix ? (
                      <CheckCircle className="h-4 w-4 text-green-500" />
                    ) : (
                      <Copy className="h-4 w-4 text-gray-400" />
                    )}
                  </button>
                </div>
                <pre className="bg-gray-900 border border-green-700/50 rounded-lg p-4 text-xs text-gray-300 overflow-x-auto max-h-96">
                  <code>{task.fix_code || 'No fix generated yet'}</code>
                </pre>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Full Original Code */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4 text-red-500" />
                    <h3 className="text-sm font-semibold text-white">Original Code (Vulnerable)</h3>
                  </div>
                  <button
                    onClick={() => handleCopy(task.original_code, 'original')}
                    className="p-1 hover:bg-gray-800 rounded transition-colors"
                  >
                    {copiedOriginal ? (
                      <CheckCircle className="h-4 w-4 text-green-500" />
                    ) : (
                      <Copy className="h-4 w-4 text-gray-400" />
                    )}
                  </button>
                </div>
                <pre className="bg-gray-900 border border-red-700/50 rounded-lg p-4 text-xs text-gray-300 overflow-x-auto">
                  <code>{task.original_code}</code>
                </pre>
              </div>

              {/* Full Fixed Code */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Check className="h-4 w-4 text-green-500" />
                    <h3 className="text-sm font-semibold text-white">Fixed Code (Secure)</h3>
                  </div>
                  <button
                    onClick={() => handleCopy(task.fix_code || '', 'fix')}
                    className="p-1 hover:bg-gray-800 rounded transition-colors"
                  >
                    {copiedFix ? (
                      <CheckCircle className="h-4 w-4 text-green-500" />
                    ) : (
                      <Copy className="h-4 w-4 text-gray-400" />
                    )}
                  </button>
                </div>
                <pre className="bg-gray-900 border border-green-700/50 rounded-lg p-4 text-xs text-gray-300 overflow-x-auto">
                  <code>{task.fix_code || 'No fix generated yet'}</code>
                </pre>
              </div>
            </div>
          )}

          {/* Test Code */}
          {task.test_code && (
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <TestTube className="h-4 w-4 text-purple-500" />
                <h3 className="text-sm font-semibold text-white">Generated Test</h3>
              </div>
              <pre className="bg-gray-900 border border-purple-700/50 rounded-lg p-4 text-xs text-gray-300 overflow-x-auto max-h-64">
                <code>{task.test_code}</code>
              </pre>
            </div>
          )}

          {/* Fix Explanation */}
          {task.fix_explanation && (
            <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
              <h3 className="text-sm font-semibold text-white mb-2">What Changed?</h3>
              <p className="text-sm text-gray-300">{task.fix_explanation}</p>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="px-6 py-4 border-t border-gray-800 bg-gray-800/30">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={createPR}
                  onChange={(e) => setCreatePR(e.target.checked)}
                  className="w-4 h-4 rounded border-gray-600 bg-gray-800 text-blue-600 focus:ring-2 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-300">Create Pull Request after approval</span>
              </label>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={handleReject}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors flex items-center gap-2"
              >
                <X className="h-4 w-4" />
                Reject Fix
              </button>
              <button
                onClick={handleApprove}
                className="px-6 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors flex items-center gap-2 font-medium"
              >
                <Check className="h-4 w-4" />
                Approve {createPR ? '& Create PR' : 'Fix'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
