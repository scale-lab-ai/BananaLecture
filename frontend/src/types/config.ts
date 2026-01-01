// Config类型定义

export interface EnvConfig {
  LLM_OPENAI_API_KEY: string;
  LLM_OPENAI_BASE_URL: string;
  LLM_OPENAI_MODEL: string;
  MINIMAX_AUDIO_API_KEY: string;
  MINIMAX_AUDIO_GROUP_ID: string;
  MINIMAX_AUDIO_MODEL: string;
}

export interface RoleConfig {
  [key: string]: string;
}

export interface Config {
  env: EnvConfig;
  roles: RoleConfig;
}

// API 请求/响应类型
export interface GetEnvConfigResponse {
  LLM_OPENAI_API_KEY: string;
  LLM_OPENAI_BASE_URL: string;
  LLM_OPENAI_MODEL: string;
  MINIMAX_AUDIO_API_KEY: string;
  MINIMAX_AUDIO_GROUP_ID: string;
  MINIMAX_AUDIO_MODEL: string;
}

export interface UpdateEnvConfigRequest {
  LLM_OPENAI_API_KEY?: string;
  LLM_OPENAI_BASE_URL?: string;
  LLM_OPENAI_MODEL?: string;
  MINIMAX_AUDIO_API_KEY?: string;
  MINIMAX_AUDIO_GROUP_ID?: string;
  MINIMAX_AUDIO_MODEL?: string;
}

export interface UpdateEnvConfigResponse {
  message: string;
}

export interface GetRolesConfigResponse {
  [key: string]: string;
}

export interface UpdateRolesConfigRequest {
  [key: string]: string;
}

export interface UpdateRolesConfigResponse {
  message: string;
}
