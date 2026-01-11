import type { Script } from './script';

// 项目相关类型定义

export interface Project {
  id: string;
  name: string;
  pdf_path: string;
  images: Image[];
  created_at: string;
  updated_at: string;
}

export interface Image {
  id: string;
  img_path: string;
  script?: Script;
}

export interface CreateProjectRequest {
  name: string;
}

export interface CreateProjectResponse {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
}

export interface UploadPdfResponse {
  message: string;
  pdf_path: string;
}

export interface GetProjectsResponse {
  projects: Project[];
}

export interface GetProjectResponse {
  message: string;
  project: Project;
}

export interface UpdateProjectRequest {
  name: string;
}

export interface UpdateProjectResponse {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
}

export interface DeleteProjectResponse {
  message: string;
}

export interface ConvertPdfResponse {
  message: string;
  images: Image[];
  task_id?: string;
}

// 获取图片相关类型
export interface GetImageResponse {
  imageBlob: Blob;
  imageUrl: string;
}

// 项目操作相关类型
export interface ProjectOperation {
  type: 'rename' | 'delete';
  projectId: string;
  projectName?: string;
}

export interface ProjectMenuItem {
  key: string;
  label: string;
  icon?: React.ReactNode;
  children?: ProjectMenuItem[];
}