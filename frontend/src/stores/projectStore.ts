import { create } from 'zustand';
import type { Project, Script, ProjectOperation } from '../types';
import {
  getProjects,
  getProject,
  createProject,
  updateProject,
  deleteProject,
  uploadPdf,
  convertPdf,
  downloadPpt,
  getImage
} from '../services/projectService';
import { getScript } from '../services/scriptService';
import { useTaskStore } from './taskStore';

interface ProjectState {
  projects: Project[];
  isLoading: boolean;
  error: string | null;

  currentProject: Project | null;
  isCurrentLoading: boolean;
  currentError: string | null;

  currentPageScript: Script | null;
  isScriptLoading: boolean;
  scriptError: string | null;

  currentPageImage: string | null;
  isImageLoading: boolean;
  imageError: string | null;

  currentPageNumber: number;

  imageCache: Map<string, string>;

  isCreatingProject: boolean;
  isUpdatingProject: boolean;
  isDeletingProject: boolean;

  // PDF conversion progress
  pdfConversionTaskId: string | null;
  pdfConversionProgress: number;
  isPdfConverting: boolean;
  
  // 操作方法
  fetchProjects: () => Promise<void>;
  fetchProject: (projectId: string) => Promise<void>;
  createProject: (name: string) => Promise<Project | null>;
  updateProject: (projectId: string, name: string) => Promise<void>;
  deleteProject: (projectId: string) => Promise<void>;
  setCurrentProject: (project: Project | null) => void;
  uploadPdf: (projectId: string, file: File) => Promise<void>;
  uploadPdfAndConvert: (projectId: string, file: File) => Promise<void>;
  convertPdf: (projectId: string) => Promise<void>;
  downloadPpt: (projectId: string) => Promise<Blob | null>;// 获取图片
  getImage: (projectId: string, pageNumber: number) => Promise<void>;
  getScript: (projectId: string, pageNumber: number) => Promise<void>;
  setCurrentPage: (pageNumber: number) => void;
  clearErrors: () => void;
  
  // 项目操作方法
  handleProjectOperation: (operation: ProjectOperation) => Promise<void>;
  refreshCurrentProject: () => Promise<void>;
}

// 创建项目状态管理
export const useProjectStore = create<ProjectState>((set, get) => ({
  // 项目列表
  projects: [],
  isLoading: false,
  error: null,
  
  // 当前选中的项目
  currentProject: null,
  isCurrentLoading: false,
  currentError: null,
  
  // 当前页面的脚本
  currentPageScript: null,
  isScriptLoading: false,
  scriptError: null,
  
  // 当前页面的图片
  currentPageImage: null,
  isImageLoading: false,
  imageError: null,
  
  // 当前页码
  currentPageNumber: 1,

  // 图像缓存
  imageCache: new Map<string, string>(),

  // 项目操作状态
  isCreatingProject: false,
  isUpdatingProject: false,
  isDeletingProject: false,

  // PDF conversion progress
  pdfConversionTaskId: null,
  pdfConversionProgress: 0,
  isPdfConverting: false,
  
  // 获取项目列表
  fetchProjects: async () => {
    set({ isLoading: true, error: null });
    try {
      const data = await getProjects();
      set({ projects: data.projects, isLoading: false });
    } catch (error) {
      set({ 
        error: error instanceof Error ? error.message : '获取项目列表失败', 
        isLoading: false 
      });
    }
  },
  
  // 获取项目详情
  fetchProject: async (projectId: string) => {
    set({ isCurrentLoading: true, currentError: null });
    try {
      const data = await getProject(projectId);
      set({ 
        currentProject: data.project, 
        isCurrentLoading: false,
        currentPageNumber: 1,
        currentPageScript: null
      });
    } catch (error) {
      set({ 
        currentError: error instanceof Error ? error.message : '获取项目详情失败', 
        isCurrentLoading: false 
      });
    }
  },
  
  // 创建项目
  createProject: async (name: string) => {
    set({ isCreatingProject: true, error: null });
    try {
      const data = await createProject({ name });
      const newProject: Project = {
        id: data.id,
        name: data.name,
        pdf_path: '',
        images: [],
        created_at: data.created_at,
        updated_at: data.updated_at
      };
      
      // 更新项目列表
      const { projects } = get();
      set({ 
        projects: [...projects, newProject],
        isCreatingProject: false
      });
      
      return newProject;
    } catch (error) {
      set({ 
        error: error instanceof Error ? error.message : '创建项目失败', 
        isCreatingProject: false
      });
      return null;
    }
  },
  
  // 更新项目
  updateProject: async (projectId: string, name: string) => {
    set({ isUpdatingProject: true, error: null });
    try {
      await updateProject(projectId, { name });
      
      // 更新项目列表中的项目
      const { projects, currentProject } = get();
      const updatedProjects = projects.map(project => 
        project.id === projectId 
          ? { ...project, name, updated_at: new Date().toISOString() }
          : project
      );
      
      set({ 
        projects: updatedProjects,
        isUpdatingProject: false
      });
      
      // 如果是当前项目，也更新当前项目
      if (currentProject && currentProject.id === projectId) {
        set({ 
          currentProject: { ...currentProject, name, updated_at: new Date().toISOString() }
        });
      }
    } catch (error) {
      set({ 
        error: error instanceof Error ? error.message : '更新项目失败', 
        isUpdatingProject: false
      });
    }
  },
  
  // 删除项目
  deleteProject: async (projectId: string) => {
    set({ isDeletingProject: true, error: null });
    try {
      await deleteProject(projectId);
      
      // 从项目列表中移除
      const { projects, currentProject } = get();
      const updatedProjects = projects.filter(project => project.id !== projectId);
      
      set({ 
        projects: updatedProjects,
        isDeletingProject: false
      });
      
      // 如果删除的是当前项目，清空当前项目
      if (currentProject && currentProject.id === projectId) {
        set({ 
          currentProject: null,
          currentPageScript: null,
          currentPageNumber: 1
        });
      }
    } catch (error) {
      set({ 
        error: error instanceof Error ? error.message : '删除项目失败', 
        isDeletingProject: false
      });
    }
  },
  
  // 设置当前项目
  setCurrentProject: (project: Project | null) => {
    set({ 
      currentProject: project,
      currentPageScript: null,
      currentPageImage: null,
      currentPageNumber: 1,
      currentError: null,
      imageError: null
    });
  },
  
  // 上传PDF
  uploadPdf: async (projectId: string, file: File) => {
    set({ isCurrentLoading: true, currentError: null });
    try {
      await uploadPdf(projectId, file);
      
      // 重新获取项目详情以更新PDF路径
      await get().fetchProject(projectId);
    } catch (error) {
      set({ 
        currentError: error instanceof Error ? error.message : '上传PDF失败', 
        isCurrentLoading: false 
      });
    }
  },

  // 上传PDF并自动切分
  uploadPdfAndConvert: async (projectId: string, file: File) => {
    set({ isCurrentLoading: true, currentError: null, isPdfConverting: true, pdfConversionProgress: 0 });
    try {
      // 第一步：上传PDF
      await uploadPdf(projectId, file);

      // 第二步：切分PDF为图片
      const response = await convertPdf(projectId);

      // If task_id is returned, monitor progress
      if (response.task_id) {
        set({ pdfConversionTaskId: response.task_id });

        // Start monitoring task progress
        const taskStore = useTaskStore.getState();
        taskStore.startMonitoring(response.task_id);

        // Add listener to update progress
        const progressListener = (progress: any) => {
          if (progress.taskId === response.task_id) {
            set({ pdfConversionProgress: progress.progress * 100 });

            // If task is completed or failed, refresh project data
            if (progress.status === 'completed' || progress.status === 'failed') {
              set({ isPdfConverting: false });
              get().fetchProject(projectId).catch(error => {
                console.error('Failed to refresh project after PDF conversion:', error);
              });
            }
          }
        };

        taskStore.addTaskListener(progressListener);

        // Clean up listener when task is done
        const checkTaskStatus = setInterval(() => {
          const task = taskStore.tasks?.find(t => t.id === response.task_id);
          if (task && (task.status === 'completed' || task.status === 'failed')) {
            clearInterval(checkTaskStatus);
            taskStore.removeTaskListener(progressListener);
          }
        }, 1000);
      } else {
        // Fallback to old behavior if no task_id
        await get().fetchProject(projectId);
        set({ isPdfConverting: false });
      }
    } catch (error) {
      set({
        currentError: error instanceof Error ? error.message : '上传PDF或切分失败',
        isCurrentLoading: false,
        isPdfConverting: false
      });
      throw error;
    }
  },
  
  // PDF转图片
  convertPdf: async (projectId: string) => {
    set({ isCurrentLoading: true, currentError: null, isPdfConverting: true, pdfConversionProgress: 0 });
    try {
      // Call API to start conversion
      const response = await convertPdf(projectId);

      // If task_id is returned, monitor progress
      if (response.task_id) {
        set({ pdfConversionTaskId: response.task_id });

        // Start monitoring task progress
        const taskStore = useTaskStore.getState();
        taskStore.startMonitoring(response.task_id);

        // Add listener to update progress
        const progressListener = (progress: any) => {
          if (progress.taskId === response.task_id) {
            set({ pdfConversionProgress: progress.progress * 100 });

            // If task is completed or failed, refresh project data
            if (progress.status === 'completed' || progress.status === 'failed') {
              set({ isPdfConverting: false });
              get().fetchProject(projectId).catch(error => {
                console.error('Failed to refresh project after PDF conversion:', error);
              });
            }
          }
        };

        taskStore.addTaskListener(progressListener);

        // Clean up listener when task is done
        const checkTaskStatus = setInterval(() => {
          const task = taskStore.tasks?.find(t => t.id === response.task_id);
          if (task && (task.status === 'completed' || task.status === 'failed')) {
            clearInterval(checkTaskStatus);
            taskStore.removeTaskListener(progressListener);
          }
        }, 1000);
      } else {
        // Fallback to old behavior if no task_id
        await get().fetchProject(projectId);
        set({ isPdfConverting: false });
      }
    } catch (error) {
      set({
        currentError: error instanceof Error ? error.message : 'PDF转图片失败',
        isCurrentLoading: false,
        isPdfConverting: false
      });
    }
  },
  
  // 下载PPT
  downloadPpt: async (projectId: string) => {
    try {
      const blob = await downloadPpt(projectId);
      return blob;
    } catch (error) {
      set({ 
        error: error instanceof Error ? error.message : '下载PPT失败'
      });
      return null;
    }
  },
  
  // 获取图片
  getImage: async (projectId: string, pageNumber: number) => {
    const cacheKey = `${projectId}-${pageNumber}`;
    const { imageCache } = get();

    if (imageCache.has(cacheKey)) {
      set({
        currentPageImage: imageCache.get(cacheKey) || null,
        isImageLoading: false
      });
      return;
    }

    set({ isImageLoading: true, imageError: null });
    try {
      const data = await getImage(projectId, pageNumber);
      imageCache.set(cacheKey, data.imageUrl);
      set({
        currentPageImage: data.imageUrl,
        isImageLoading: false,
        imageCache
      });
    } catch (error) {
      set({
        imageError: error instanceof Error ? error.message : '获取图片失败',
        isImageLoading: false
      });
    }
  },
  
  // 获取脚本
  getScript: async (projectId: string, pageNumber: number) => {
    set({ isScriptLoading: true, scriptError: null });
    try {
      const data = await getScript(projectId, pageNumber);
      set({ 
        currentPageScript: data.script, 
        isScriptLoading: false
      });
    } catch (error) {
      set({ 
        scriptError: error instanceof Error ? error.message : '获取脚本失败', 
        isScriptLoading: false 
      });
    }
  },
  
  // 设置当前页码
  setCurrentPage: (pageNumber: number) => {
    set({
      currentPageNumber: pageNumber,
      currentPageScript: null
    });
  },
  
  // 清除错误
  clearErrors: () => {
    set({ 
      error: null,
      currentError: null,
      scriptError: null,
      imageError: null
    });
  },
  
  // 项目操作方法
  handleProjectOperation: async (operation: ProjectOperation) => {
    const { type, projectId, projectName } = operation;
    
    if (type === 'rename' && projectName) {
      await get().updateProject(projectId, projectName);
    } else if (type === 'delete') {
      await get().deleteProject(projectId);
    }
  },
  
  // 刷新当前项目
  refreshCurrentProject: async () => {
    const { currentProject } = get();
    if (currentProject) {
      await get().fetchProject(currentProject.id);
    }
  }
}));