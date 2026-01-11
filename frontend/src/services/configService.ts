import api from './api';
import type {
  GetEnvConfigResponse,
  UpdateEnvConfigRequest,
  UpdateEnvConfigResponse,
  GetRolesConfigResponse,
  GetVoiceSettingsResponse,
  VoiceSettingCreateRequest,
  VoiceSettingUpdateRequest,
  GetRoleListResponse,
  RoleCreateRequest,
  MessageResponse,
  VoiceGroupListResponse,
  VoiceGroupCreateRequest,
  VoiceGroupUpdateRequest,
  CurrentGroupResponse
} from '../types/config';

// Get environment configuration
export const getEnvConfig = async (): Promise<GetEnvConfigResponse> => {
  return api.get('/config/env');
};

// Update environment configuration
export const updateEnvConfig = async (config: UpdateEnvConfigRequest): Promise<UpdateEnvConfigResponse> => {
  return api.put('/config/env', config);
};

// Get role configuration
export const getRoleConfig = async (): Promise<GetRolesConfigResponse> => {
  return api.get('/config/roles');
};

// Get all voice settings
export const getVoiceSettings = async (): Promise<GetVoiceSettingsResponse> => {
  return api.get('/config/voices');
};

// Add a new voice setting
export const addVoiceSetting = async (voiceSetting: VoiceSettingCreateRequest): Promise<MessageResponse> => {
  return api.post('/config/voices', voiceSetting);
};

// Update a voice setting
export const updateVoiceSetting = async (voiceId: string, updates: VoiceSettingUpdateRequest): Promise<MessageResponse> => {
  return api.put(`/config/voices/${voiceId}`, updates);
};

// Delete a voice setting
export const deleteVoiceSetting = async (voiceId: string): Promise<MessageResponse> => {
  return api.delete(`/config/voices/${voiceId}`);
};

// Get role list
export const getRoleList = async (): Promise<GetRoleListResponse> => {
  return api.get('/config/roles/list');
};

// Add a new role
export const addRole = async (role: RoleCreateRequest): Promise<MessageResponse> => {
  return api.post('/config/roles', role);
};

// Delete a role
export const deleteRole = async (roleName: string): Promise<MessageResponse> => {
  return api.delete(`/config/roles/${encodeURIComponent(roleName)}`);
};

// Rename a role
export const renameRole = async (oldName: string, newName: string): Promise<MessageResponse> => {
  return api.put(`/config/roles/${encodeURIComponent(oldName)}/rename`, { new_name: newName });
};

// Update role voice
export const updateRoleVoice = async (roleName: string, voiceId: string): Promise<MessageResponse> => {
  return api.put(`/config/roles/${encodeURIComponent(roleName)}/voice`, { voice_id: voiceId });
};

// Get all voice groups
export const getAllGroups = async (): Promise<VoiceGroupListResponse> => {
  return api.get('/config/groups');
};

// Add a new voice group
export const addGroup = async (group: VoiceGroupCreateRequest): Promise<MessageResponse> => {
  return api.post('/config/groups', group);
};

// Update a voice group
export const updateGroup = async (groupName: string, updates: VoiceGroupUpdateRequest): Promise<MessageResponse> => {
  return api.put(`/config/groups/${encodeURIComponent(groupName)}`, updates);
};

// Delete a voice group
export const deleteGroup = async (groupName: string): Promise<MessageResponse> => {
  return api.delete(`/config/groups/${encodeURIComponent(groupName)}`);
};

// Get current group
export const getCurrentGroup = async (): Promise<CurrentGroupResponse> => {
  return api.get('/config/current-group');
};

// Set current group
export const setCurrentGroup = async (groupName: string): Promise<MessageResponse> => {
  return api.put('/config/current-group', { group_name: groupName });
};
