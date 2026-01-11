// Config type definitions

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

// Voice setting types
export interface VoiceSetting {
  voice_id: string;
  name: string;
  gender: string;
  age_group: string;
  language: string;
  description: string;
  example_url: string;
}

export interface RoleItem {
  name: string;
  voice_id: string;
}

// API request/response types
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

export interface GetVoiceSettingsResponse {
  voices: VoiceSetting[];
}

export interface VoiceSettingCreateRequest {
  voice_id: string;
  name: string;
  gender: string;
  age_group: string;
  language: string;
  description?: string;
  example_url?: string;
}

export interface VoiceSettingUpdateRequest {
  name?: string;
  gender?: string;
  age_group?: string;
  language?: string;
  description?: string;
  example_url?: string;
}

export interface GetRoleListResponse {
  roles: RoleItem[];
}

export interface RoleCreateRequest {
  name: string;
  voice_id?: string;
}

export interface RoleRenameRequest {
  new_name: string;
}

export interface MessageResponse {
  message: string;
}

export interface VoiceGroup {
  name: string;
  role: { [key: string]: string };
}

export interface VoiceGroupCreateRequest {
  name: string;
  role?: { [key: string]: string };
}

export interface VoiceGroupUpdateRequest {
  name?: string;
  role?: { [key: string]: string };
}

export interface VoiceGroupListResponse {
  groups: VoiceGroup[];
}

export interface CurrentGroupResponse {
  current_group: string;
}

export interface SetCurrentGroupRequest {
  group_name: string;
}
