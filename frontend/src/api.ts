import axios from 'axios';
import type { AxiosInstance } from 'axios';
import { mockRepositories, mockTasks } from './data/mockData';

const api: AxiosInstance = axios.create({
    baseURL: 'http://localhost:8000/api/v1/',
    timeout: 5000, // 5 second timeout
});

// Flag to check if backend is available
let backendAvailable: boolean = true;

// Test backend connectivity
export const testBackendConnection = async () => {
    try {
        await api.get('sessions/', { timeout: 2000 });
        backendAvailable = true;
        return true;
    } catch (error) {
        backendAvailable = false;
        console.warn('Backend not available, using mock data');
        return false;
    }
};

// Initialize connection test
testBackendConnection();

// ============================================
// ANALYSIS SESSIONS API
// ============================================

export const getSessions = async () => {
    try {
        const response = await api.get('sessions/');
        return response.data;
    } catch (error) {
        console.warn('Using mock sessions data');
        // Fallback to mock data
        return {
            sessions: mockRepositories.slice(0, 10).map(repo => ({
                id: `session-${repo.id}`,
                repository_name: `${repo.owner}/${repo.name}`,
                status: repo.status,
                files_analyzed: repo.files_analyzed,
                vulnerabilities_found: repo.vulnerabilities_found,
                prs_created: repo.prs_created,
                started_at: repo.started_at,
            })),
            summary: {
                total_scans: mockRepositories.filter(r => r.status === 'completed').length,
                total_files: mockRepositories.reduce((sum, r) => sum + r.files_analyzed, 0),
                total_vulnerabilities: mockRepositories.reduce((sum, r) => sum + r.vulnerabilities_found, 0),
                total_prs: mockRepositories.reduce((sum, r) => sum + r.prs_created, 0),
            }
        };
    }
};

export const getSessionStatus = async (sessionId: string) => {
    try {
        const response = await api.get(`sessions/${sessionId}/status/`);
        return response.data;
    } catch (error) {
        console.warn('Using mock session status');
        // Fallback to mock data
        const mockRepo = mockRepositories[0];
        return {
            session_id: sessionId,
            repository: {
                id: mockRepo.id,
                name: mockRepo.name,
                url: mockRepo.url,
            },
            status: 'running',
            progress: {
                total_files: 150,
                files_analyzed: 75,
                files_failed: 2,
                percentage: 50,
            },
            results: {
                vulnerabilities_found: 12,
                tasks_created: 12,
                prs_created: 5,
            },
            timestamps: {
                started_at: new Date().toISOString(),
                completed_at: null,
                last_checkpoint_at: new Date().toISOString(),
            },
            estimated_time_remaining_seconds: 300,
        };
    }
};

export const resumeSession = async (sessionId: string) => {
    try {
        const response = await api.post(`sessions/${sessionId}/resume/`);
        return response.data;
    } catch (error) {
        throw new Error('Failed to resume session');
    }
};

// ============================================
// REPOSITORY API
// ============================================

export const startAnalysis = async (repoUrl: string, createPrs: boolean = false) => {
    try {
        const response = await api.post('repositories/', {
            repo_url: repoUrl,
            create_prs: createPrs
        });
        return response.data;
    } catch (error: any) {
        throw new Error(error.response?.data?.error || 'Failed to start analysis');
    }
};

export const getRepositoryTasks = async (repositoryId: number) => {
    try {
        const response = await api.get(`repositories/${repositoryId}/tasks/`);
        return response.data;
    } catch (error) {
        console.warn('Using mock repository tasks');
        return {
            repository_id: repositoryId,
            total_task: mockTasks.length,
            tasks: mockTasks,
        };
    }
};

export const createPRsForRepository = async (repositoryId: number) => {
    try {
        const response = await api.post(`repositories/${repositoryId}/pull-requests/`);
        return response.data;
    } catch (error) {
        throw new Error('Failed to create PRs');
    }
};

// ============================================
// TASK API
// ============================================

export const getTaskDetails = async (taskId: number) => {
    try {
        const response = await api.get(`tasks/${taskId}/`);
        return response.data;
    } catch (error) {
        console.warn('Using mock task details');
        const mockTask = mockTasks.find(t => t.id === taskId) || mockTasks[0];
        return mockTask;
    }
};

export const getTaskStatus = async (taskId: string) => {
    try {
        const response = await api.get(`tasks/${taskId}/status/`);
        return response.data;
    } catch (error) {
        return {
            task_id: taskId,
            status: 'SUCCESS',
            result: { message: 'Task completed' }
        };
    }
};

export const verifyAndFix = async (taskId: number, createPR: boolean = false) => {
    try {
        const response = await api.post(`tasks/${taskId}/verify-and-fix/`, {
            create_pr: createPR,
        });
        return response.data;
    } catch (error) {
        throw new Error('Failed to verify and fix');
    }
};

// ============================================
// UTILITY
// ============================================

export const isBackendAvailable = () => backendAvailable;

export default api;

// ============================================
// FIX GENERATION API (NEW)
// ============================================

export const generateFix = async (taskId: number, createPR: boolean = false) => {
    try {
        const response = await api.post(`tasks/${taskId}/generate-fix/`, {
            create_pr: createPR
        });
        return response.data;
    } catch (error: any) {
        throw new Error(error.response?.data?.error || 'Failed to generate fix');
    }
};

export const processAllTasks = async (sessionId: string, createPR: boolean = false) => {
    try {
        const response = await api.post(`sessions/${sessionId}/process-all/`, {
            create_pr: createPR
        });
        return response.data;
    } catch (error: any) {
        throw new Error(error.response?.data?.error || 'Failed to process tasks');
    }
};

export const getTaskDetail = async (taskId: number) => {
    try {
        const response = await api.get(`tasks/${taskId}/`);
        return response.data;
    } catch (error: any) {
        throw new Error(error.response?.data?.error || 'Failed to get task details');
    }
};
