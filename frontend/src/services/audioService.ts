import api from './api';
import type {
  BatchGenerateAudioRequest,
  BatchGenerateAudioResponse,
  GeneratePageAudioRequest,
  GeneratePageAudioResponse,
  GenerateDialogueAudioRequest,
  GenerateDialogueAudioResponse,
  GetPageAudioResponse,
  GetDialogueAudioResponse
} from '../types/audio';

// 批量生成音频
export const batchGenerateAudio = async (data: BatchGenerateAudioRequest): Promise<BatchGenerateAudioResponse> => {
  return api.post('/audio/batch-generate', data);
};

// 指定页面生成音频
export const generatePageAudio = async (data: GeneratePageAudioRequest): Promise<GeneratePageAudioResponse> => {
  return api.post('/audio/page/generate', data);
};

// 指定对话生成音频
export const generateDialogueAudio = async (data: GenerateDialogueAudioRequest): Promise<GenerateDialogueAudioResponse> => {
  return api.post('/audio/dialogue/generate', data);
};

// 获取音频文件
export const getPageAudio = async (projectId: string, pageNumber: number): Promise<GetPageAudioResponse> => {
  return api.get(`/audio/${projectId}/${pageNumber}/file`, {
    responseType: 'blob'
  });
};

// 获取对话音频文件
export const getDialogueAudio = async (
  projectId: string,
  pageNumber: number,
  dialogueId: string
): Promise<GetDialogueAudioResponse> => {
  return api.get(`/audio/${projectId}/${pageNumber}/${dialogueId}/audio-file`, {
    responseType: 'blob'
  });
};