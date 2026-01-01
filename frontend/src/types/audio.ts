// 音频相关类型定义

import type { DialogueItem } from './script';

// API 请求/响应类型
export interface BatchGenerateAudioRequest {
  project_id: string;
}

export interface BatchGenerateAudioResponse {
  message: string;
  task_id: string;
}

export interface GeneratePageAudioRequest {
  project_id: string;
  page_number: number;
}

export interface GeneratePageAudioResponse {
  message: string;
  task_id: string;
}

export interface GenerateDialogueAudioRequest {
  project_id: string;
  page_number: number;
  dialogue_id: string;
}

export interface GenerateDialogueAudioResponse {
  message: string;
  dialogue: DialogueItem;
}

export interface GetPageAudioResponse {
  data: Blob;
}

export interface GetDialogueAudioResponse {
  data: Blob;
}

// 音频播放相关类型
export interface AudioPlayerState {
  isPlaying: boolean;
  currentTime: number;
  duration: number;
  volume: number;
}

export interface AudioControls {
  play: () => void;
  pause: () => void;
  seek: (time: number) => void;
  setVolume: (volume: number) => void;
}