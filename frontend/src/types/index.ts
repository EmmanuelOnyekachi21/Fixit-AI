export type AnalysisStatus = 'pending' | 'running' | 'completed' | 'failed';
export type Severity = 'critical' | 'high' | 'medium' | 'low';
export type TaskStatus = 'pending' | 'processing' | 'completed' | 'failed' | 'false_positive' | 'pr_created';
export type FixStatus = 'pending' | 'generated' | 'verified' | 'failed' | 'pr_created' | 'pr_failed';
export type TestStatus = 'pending' | 'generated' | 'passed' | 'failed' | 'error';

export interface Repository {
  id: number;
  name: string;
  owner: string;
  url: string;
  status: AnalysisStatus;
  files_analyzed: number;
  vulnerabilities_found: number;
  prs_created: number;
  started_at: string;
}

export interface Task {
  id: number;
  vulnerability_type: string;
  severity: Severity;
  file_path: string;
  line_number: number;
  description: string;
  test_code: string;
  fix_code: string;
  original_code: string;
  status: TaskStatus;
  test_status: TestStatus;
  fix_status: FixStatus;
  pr_url?: string;
  validation_message?: string;
  retry_count?: number;
}

export interface AnalysisSession {
  session_id: string;
  repository_id: number;
  status: AnalysisStatus;
  total_files: number;
  files_analyzed: number;
  vulnerabilities_found: number;
  progress_percentage: number;
  estimated_time_remaining: number;
  current_file?: string;
  logs: LogEntry[];
}

export interface LogEntry {
  id: number;
  timestamp: string;
  message: string;
  type: 'success' | 'error' | 'info' | 'warning';
}
