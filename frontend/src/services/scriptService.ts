import api from './api';
import type {
  BatchGenerateScriptRequest,
  BatchGenerateScriptResponse,
  GenerateScriptRequest,
  GenerateScriptResponse,
  GetScriptResponse,
  UpdateScriptRequest,
  UpdateScriptResponse,
  UpdateDialogueRequest,
  UpdateDialogueResponse,
  AddDialogueRequest,
  AddDialogueResponse,
  DeleteDialogueResponse
} from '../types/script';

// 批量生成脚本
export const batchGenerateScript = async (data: BatchGenerateScriptRequest): Promise<BatchGenerateScriptResponse> => {
  return api.post('/scripts/batch-generate', data);
};

// 指定页面生成脚本
export const generateScript = async (data: GenerateScriptRequest): Promise<GenerateScriptResponse> => {
  return api.post('/scripts/generate', data);
};

// 获取脚本
export const getScript = async (projectId: string, pageNumber: number): Promise<GetScriptResponse> => {
  return api.get(`/scripts/${projectId}/${pageNumber}`);
};

// 更新脚本
export const updateScript = async (projectId: string, pageNumber: number, data: UpdateScriptRequest): Promise<UpdateScriptResponse> => {
  return api.put(`/scripts/${projectId}/${pageNumber}`, data);
};

// 更新对话项
export const updateDialogue = async (
  projectId: string,
  pageNumber: number,
  dialogueId: string,
  data: UpdateDialogueRequest
): Promise<UpdateDialogueResponse> => {
  return api.put(`/dialogues/${projectId}/${pageNumber}/${dialogueId}`, data);
};

// 添加对话项
export const addDialogue = async (
  projectId: string,
  pageNumber: number,
  data: AddDialogueRequest
): Promise<AddDialogueResponse> => {
  return api.post(`/dialogues/${projectId}/${pageNumber}`, data);
};

// 删除对话项
export const deleteDialogue = async (
  projectId: string,
  pageNumber: number,
  dialogueId: string
): Promise<DeleteDialogueResponse> => {
  return api.delete(`/dialogues/${projectId}/${pageNumber}/${dialogueId}`);
};

// 移动对话项
export const moveDialogue = async (
  projectId: string,
  pageNumber: number,
  dialogueId: string,
  direction: string
): Promise<UpdateDialogueResponse> => {
  return api.put(`/dialogues/${projectId}/${pageNumber}/${dialogueId}/move`, { direction });
};