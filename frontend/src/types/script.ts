// 脚本相关类型定义

export interface DialogueItem {
  id: string;
  role: DialogueRole;
  content: string;
  emotion: EmotionType;
  speed: SpeechSpeed;
  created_at: string;
  updated_at: string;
}

export interface Script {
  id: string;
  page_number: number;
  dialogues: DialogueItem[];
}

// 枚举类型定义
export type DialogueRole = "旁白" | "大雄" | "哆啦A梦" | "道具" | "其他男声" | "其他女声" | "其他";
export type EmotionType = "auto" | "happy" | "sad" | "angry" | "fearful" | "disgusted" | "surprised" | "neutral" | "fluent";
export type SpeechSpeed = "慢" | "正常" | "快";

// API 请求/响应类型
export interface BatchGenerateScriptRequest {
  project_id: string;
}

export interface BatchGenerateScriptResponse {
  message: string;
  task_id: string;
}

export interface GenerateScriptRequest {
  project_id: string;
  page_number: number;
}

export interface GenerateScriptResponse {
  message: string;
  script: Script;
}

export interface GetScriptResponse {
  message: string;
  script: Script;
}

export interface UpdateScriptRequest {
  dialogues: Partial<DialogueItem>[];
}

export interface UpdateScriptResponse {
  message: string;
  script: Script;
}

export interface UpdateDialogueRequest {
  role: DialogueRole;
  content: string;
  emotion: EmotionType;
  speed: SpeechSpeed;
}

export interface UpdateDialogueResponse {
  id: string;
  role: DialogueRole;
  content: string;
  emotion: EmotionType;
  speed: SpeechSpeed;
}

export interface AddDialogueRequest {
  role: DialogueRole;
  content: string;
  emotion: EmotionType;
  speed: SpeechSpeed;
}

export interface AddDialogueResponse {
  id: string;
  script_id: string;
  role: DialogueRole;
  content: string;
  emotion: EmotionType;
  speed: SpeechSpeed;
}

export interface DeleteDialogueResponse {
  message: string;
  dialogue: DialogueItem;
}