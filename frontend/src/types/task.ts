// 任务相关类型定义

export interface Task {
  id: string;
  type: TaskType;
  status: TaskStatus;
  progress: number; // 0.0 - 1.0
  current_step: number;
  total_steps: number;
  error_message?: string;
}

export type TaskType = "script_generation" | "audio_generation" | "pdf_conversion";
export type TaskStatus = "pending" | "running" | "completed" | "failed";

// API 请求/响应类型
export interface GetTaskResponse {
  finished: boolean;
  task: Task;
}

export interface CancelTaskResponse {
  message: string;
  task_id: string;
}

// 任务进度监控相关类型
export interface TaskProgress {
  taskId: string;
  progress: number;
  status: TaskStatus;
  currentStep: number;
  totalSteps: number;
  errorMessage?: string;
}

export interface TaskMonitor {
  startMonitoring: (taskId: string) => void;
  stopMonitoring: () => void;
  getProgress: () => TaskProgress | null;
  addListener: (listener: (progress: TaskProgress) => void) => void;
  removeListener: (listener: (progress: TaskProgress) => void) => void;
}