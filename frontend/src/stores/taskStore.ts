import { create } from 'zustand';
import type { Task, TaskProgress, TaskMonitor } from '../types/task';
import { getTask, cancelTask, createTaskMonitor } from '../services/taskService';

interface TaskState {
  // 任务列表
  tasks: Task[];
  
  // 任务监控器
  monitor: TaskMonitor;
  
  // 当前正在监控的任务
  currentTaskId: string | null;
  currentTaskProgress: TaskProgress | null;
  
  // 操作方法
  getTask: (taskId: string) => Promise<Task | null>;
  cancelTask: (taskId: string) => Promise<void>;
  startMonitoring: (taskId: string) => void;
  stopMonitoring: () => void;
  addTaskListener: (listener: (progress: TaskProgress) => void) => void;
  removeTaskListener: (listener: (progress: TaskProgress) => void) => void;
  clearCurrentTask: () => void;
}

// 创建任务状态管理
export const useTaskStore = create<TaskState>((set, get) => {
  // 创建任务监控器实例
  const monitor = createTaskMonitor();
  
  return {
    // 任务列表
    tasks: [],
    
    // 任务监控器
    monitor,
    
    // 当前正在监控的任务
    currentTaskId: null,
    currentTaskProgress: null,
    
    // 获取任务
    getTask: async (taskId: string) => {
      try {
        const data = await getTask(taskId);
        
        // 更新任务列表中的任务
        const { tasks } = get();
        const existingTaskIndex = tasks.findIndex(task => task.id === taskId);
        
        if (existingTaskIndex !== -1) {
          // 更新现有任务
          const updatedTasks = [...tasks];
          updatedTasks[existingTaskIndex] = data.task;
          set({ tasks: updatedTasks });
        } else {
          // 添加新任务
          set({ tasks: [...tasks, data.task] });
        }
        
        return data.task;
      } catch (error) {
        console.error('获取任务失败:', error);
        return null;
      }
    },
    
    // 取消任务
    cancelTask: async (taskId: string) => {
      try {
        await cancelTask(taskId);
        
        // 从任务列表中移除
        const { tasks } = get();
        const updatedTasks = tasks.filter(task => task.id !== taskId);
        set({ tasks: updatedTasks });
        
        // 如果取消的是当前监控的任务，停止监控
        const { currentTaskId } = get();
        if (currentTaskId === taskId) {
          get().stopMonitoring();
        }
      } catch (error) {
        console.error('取消任务失败:', error);
      }
    },
    
    // 开始监控任务
    startMonitoring: (taskId: string) => {
      // 先停止之前的监控
      get().stopMonitoring();
      
      // 添加进度监听器
      monitor.addListener((progress: TaskProgress) => {
        set({ 
          currentTaskProgress: progress
        });
        
        // 同时更新任务列表中的任务状态
        get().getTask(taskId);
      });
      
      // 开始监控
      monitor.startMonitoring(taskId);
      set({ currentTaskId: taskId });
    },
    
    // 停止监控
    stopMonitoring: () => {
      monitor.stopMonitoring();
      set({ 
        currentTaskId: null,
        currentTaskProgress: null
      });
    },
    
    // 添加任务监听器
    addTaskListener: (listener: (progress: TaskProgress) => void) => {
      monitor.addListener(listener);
    },
    
    // 移除任务监听器
    removeTaskListener: (listener: (progress: TaskProgress) => void) => {
      monitor.removeListener(listener);
    },
    
    // 清除当前任务
    clearCurrentTask: () => {
      get().stopMonitoring();
    }
  };
});