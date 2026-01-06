import api from './api';
import type {
  CreateProjectRequest,
  CreateProjectResponse,
  UploadPdfResponse,
  GetProjectsResponse,
  GetProjectResponse,
  UpdateProjectRequest,
  UpdateProjectResponse,
  DeleteProjectResponse,
  ConvertPdfResponse,
  GetImageResponse
} from '../types/project';

// 创建项目
export const createProject = async (data: CreateProjectRequest): Promise<CreateProjectResponse> => {
  return api.post('/projects', data);
};

// 上传PDF文件
export const uploadPdf = async (projectId: string, file: File): Promise<UploadPdfResponse> => {
  const formData = new FormData();
  formData.append('pdf_file', file);
  
  return api.post(`/projects/${projectId}/upload-pdf`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
};

// 获取项目列表
export const getProjects = async (): Promise<GetProjectsResponse> => {
  return api.get('/projects');
};

// 获取项目详情
export const getProject = async (projectId: string): Promise<GetProjectResponse> => {
  return api.get(`/projects/${projectId}`);
};

// 更新项目名称
export const updateProject = async (projectId: string, data: UpdateProjectRequest): Promise<UpdateProjectResponse> => {
  return api.put(`/projects/${projectId}`, data);
};

// 删除项目
export const deleteProject = async (projectId: string): Promise<DeleteProjectResponse> => {
  return api.delete(`/projects/${projectId}`);
};

// PDF转图片
export const convertPdf = async (projectId: string): Promise<ConvertPdfResponse> => {
  return api.post(`/projects/${projectId}/convert-pdf`);
};

// 导出并下载PPT
export const downloadPpt = async (projectId: string): Promise<Blob> => {
  const response = await api.get(`/projects/${projectId}/download-ppt`, {
    responseType: 'blob'
  });
  return response.data;
};

// 导出并下载视频
export const downloadVideo = async (projectId: string): Promise<Blob> => {
  const response = await api.get(`/projects/${projectId}/download-video`, {
    responseType: 'blob',
    timeout: 600000 // 10分钟超时，视频导出可能需要较长时间
  });
  return response.data;
};

// 获取指定页面的图片
export const getImage = async (projectId: string, pageNumber: number): Promise<GetImageResponse> => {
  const response = await api.get(`/images/${projectId}/${pageNumber}`, {
    responseType: 'blob'
  });
  
  // 创建图片URL
  const imageBlob = response.data;
  const imageUrl = URL.createObjectURL(imageBlob);
  
  return {
    imageBlob,
    imageUrl
  };
};