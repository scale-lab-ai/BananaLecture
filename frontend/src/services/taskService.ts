import api from './api';
import type {
  GetTaskResponse,
  CancelTaskResponse,
  TaskProgress,
  TaskMonitor
} from '../types/task';

// 获取任务状态
export const getTask = async (taskId: string): Promise<GetTaskResponse> => {
  return api.get(`/tasks/${taskId}`);
};

// 取消任务
export const cancelTask = async (taskId: string): Promise<CancelTaskResponse> => {
  return api.delete(`/tasks/${taskId}`);
};

// 任务进度监控类
export class TaskMonitorImpl implements TaskMonitor {
  private taskId: string | null = null;
  private intervalId: number | null = null;
  private progress: TaskProgress | null = null;
  private listeners: ((progress: TaskProgress) => void)[] = [];

  // 开始监控任务
  startMonitoring(taskId: string): void {
    this.taskId = taskId;
    
    // 立即获取一次状态
    this.updateProgress();
    
    // 设置定时器，每2秒更新一次进度
    this.intervalId = setInterval(() => {
      this.updateProgress();
    }, 2000);
  }

  // 停止监控任务
  stopMonitoring(): void {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
    this.taskId = null;
    this.progress = null;
  }

  // 获取当前进度
  getProgress(): TaskProgress | null {
    return this.progress;
  }

  // 添加进度监听器
  addListener(listener: (progress: TaskProgress) => void): void {
    this.listeners.push(listener);
  }

  // 移除进度监听器
  removeListener(listener: (progress: TaskProgress) => void): void {
    const index = this.listeners.indexOf(listener);
    if (index !== -1) {
      this.listeners.splice(index, 1);
    }
  }

  // 更新进度
  private async updateProgress(): Promise<void> {
    if (!this.taskId) return;
    
    try {
      const response = await getTask(this.taskId);
      const task = response.task;
      
      this.progress = {
        taskId: task.id,
        progress: task.progress,
        status: task.status,
        currentStep: task.current_step,
        totalSteps: task.total_steps,
        errorMessage: task.error_message
      };
      
      // 通知所有监听器
      this.listeners.forEach(listener => {
        if (this.progress) {
          listener(this.progress);
        }
      });
      
      // 如果任务完成或失败，停止监控
      if (task.status === 'completed' || task.status === 'failed') {
        this.stopMonitoring();
      }
    } catch (error) {
      console.error('获取任务进度失败:', error);
    }
  }
}

// 创建任务监控实例
export const createTaskMonitor = (): TaskMonitor => {
  return new TaskMonitorImpl();
};