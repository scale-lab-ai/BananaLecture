import { create } from 'zustand';
import type { EnvConfig, RoleConfig, VoiceSetting, RoleItem, VoiceGroup } from '../types/config';
import {
  getEnvConfig, getRoleConfig, updateEnvConfig,
  getVoiceSettings, addVoiceSetting, updateVoiceSetting, deleteVoiceSetting,
  getRoleList, addRole, deleteRole, renameRole, updateRoleVoice,
  getAllGroups, addGroup, updateGroup, deleteGroup, getCurrentGroup, setCurrentGroup
} from '../services/configService';

interface ConfigState {
  // Environment configuration
  envConfig: EnvConfig;
  isEnvLoading: boolean;
  envError: string | null;

  // Role configuration
  roleConfig: RoleConfig;
  isRoleLoading: boolean;
  roleError: string | null;

  // Voice settings
  voiceSettings: VoiceSetting[];
  isVoiceLoading: boolean;
  voiceError: string | null;

  // Role list
  roleList: RoleItem[];
  isRoleListLoading: boolean;
  roleListError: string | null;

  // Voice groups
  groups: VoiceGroup[];
  isGroupsLoading: boolean;
  groupsError: string | null;
  currentGroup: string;
  isCurrentGroupLoading: boolean;
  currentGroupError: string | null;

  // Operation methods
  fetchEnvConfig: () => Promise<void>;
  updateEnvConfig: (config: EnvConfig) => Promise<void>;
  fetchRoleConfig: () => Promise<void>;
  fetchVoiceSettings: () => Promise<void>;
  addVoiceSetting: (voiceSetting: VoiceSetting) => Promise<void>;
  updateVoiceSetting: (voiceId: string, updates: Partial<VoiceSetting>) => Promise<void>;
  deleteVoiceSetting: (voiceId: string) => Promise<void>;
  fetchRoleList: () => Promise<void>;
  addRole: (roleName: string, voiceId?: string) => Promise<void>;
  deleteRole: (roleName: string) => Promise<void>;
  renameRole: (oldName: string, newName: string) => Promise<void>;
  updateRoleVoice: (roleName: string, voiceId: string) => Promise<void>;
  fetchGroups: () => Promise<void>;
  addGroup: (group: VoiceGroup) => Promise<void>;
  updateGroup: (groupName: string, updates: Partial<VoiceGroup>) => Promise<void>;
  deleteGroup: (groupName: string) => Promise<void>;
  fetchCurrentGroup: () => Promise<void>;
  setCurrentGroup: (groupName: string) => Promise<void>;
}

// Initial environment configuration
const initialEnvConfig: EnvConfig = {
  LLM_OPENAI_API_KEY: '',
  LLM_OPENAI_BASE_URL: '',
  LLM_OPENAI_MODEL: '',
  MINIMAX_AUDIO_API_KEY: '',
  MINIMAX_AUDIO_GROUP_ID: '',
  MINIMAX_AUDIO_MODEL: ''
};

// Initial role configuration
const initialRoleConfig: RoleConfig = {
  '旁白': '',
  '大雄': '',
  '哆啦A梦': '',
  '道具': '',
  '其他男声': '',
  '其他女声': '',
  '其他': ''
};

// Create configuration state management
export const useConfigStore = create<ConfigState>((set) => ({
  // Environment configuration
  envConfig: initialEnvConfig,
  isEnvLoading: false,
  envError: null,

  // Role configuration
  roleConfig: initialRoleConfig,
  isRoleLoading: false,
  roleError: null,

  // Voice settings
  voiceSettings: [],
  isVoiceLoading: false,
  voiceError: null,

  // Role list
  roleList: [],
  isRoleListLoading: false,
  roleListError: null,

  // Voice groups
  groups: [],
  isGroupsLoading: false,
  groupsError: null,
  currentGroup: 'default',
  isCurrentGroupLoading: false,
  currentGroupError: null,

  // Get environment configuration
  fetchEnvConfig: async () => {
    set({ isEnvLoading: true, envError: null });
    try {
      const data = await getEnvConfig();
      set({ envConfig: data, isEnvLoading: false });
    } catch (error) {
      set({
        envError: error instanceof Error ? error.message : 'Failed to get environment configuration',
        isEnvLoading: false
      });
    }
  },

  // Update environment configuration
  updateEnvConfig: async (config) => {
    set({ isEnvLoading: true, envError: null });
    try {
      await updateEnvConfig(config);
      set({ envConfig: config, isEnvLoading: false });
    } catch (error) {
      set({
        envError: error instanceof Error ? error.message : 'Failed to update environment configuration',
        isEnvLoading: false
      });
    }
  },

  // Get role configuration
  fetchRoleConfig: async () => {
    set({ isRoleLoading: true, roleError: null });
    try {
      const data = await getRoleConfig();
      set({ roleConfig: data, isRoleLoading: false });
    } catch (error) {
      set({
        roleError: error instanceof Error ? error.message : 'Failed to get role configuration',
        isRoleLoading: false
      });
    }
  },

  // Get voice settings
  fetchVoiceSettings: async () => {
    set({ isVoiceLoading: true, voiceError: null });
    try {
      const data = await getVoiceSettings();
      set({ voiceSettings: data.voices, isVoiceLoading: false });
    } catch (error) {
      set({
        voiceError: error instanceof Error ? error.message : 'Failed to get voice settings',
        isVoiceLoading: false
      });
    }
  },

  // Add voice setting
  addVoiceSetting: async (voiceSetting) => {
    set({ isVoiceLoading: true, voiceError: null });
    try {
      await addVoiceSetting(voiceSetting);
      set((state) => ({
        voiceSettings: [...state.voiceSettings, voiceSetting],
        isVoiceLoading: false
      }));
    } catch (error) {
      set({
        voiceError: error instanceof Error ? error.message : 'Failed to add voice setting',
        isVoiceLoading: false
      });
    }
  },

  // Update voice setting
  updateVoiceSetting: async (voiceId, updates) => {
    set({ isVoiceLoading: true, voiceError: null });
    try {
      await updateVoiceSetting(voiceId, updates);
      set((state) => ({
        voiceSettings: state.voiceSettings.map(v =>
          v.voice_id === voiceId ? { ...v, ...updates } : v
        ),
        isVoiceLoading: false
      }));
    } catch (error) {
      set({
        voiceError: error instanceof Error ? error.message : 'Failed to update voice setting',
        isVoiceLoading: false
      });
    }
  },

  // Delete voice setting
  deleteVoiceSetting: async (voiceId) => {
    set({ isVoiceLoading: true, voiceError: null });
    try {
      await deleteVoiceSetting(voiceId);
      set((state) => ({
        voiceSettings: state.voiceSettings.filter(v => v.voice_id !== voiceId),
        isVoiceLoading: false
      }));
    } catch (error) {
      set({
        voiceError: error instanceof Error ? error.message : 'Failed to delete voice setting',
        isVoiceLoading: false
      });
    }
  },

  // Get role list
  fetchRoleList: async () => {
    set({ isRoleListLoading: true, roleListError: null });
    try {
      const data = await getRoleList();
      set({ roleList: data.roles, isRoleListLoading: false });
    } catch (error) {
      set({
        roleListError: error instanceof Error ? error.message : 'Failed to get role list',
        isRoleListLoading: false
      });
    }
  },

  // Add role
  addRole: async (roleName, voiceId = '') => {
    set({ isRoleListLoading: true, roleListError: null });
    try {
      await addRole({ name: roleName, voice_id: voiceId });
      set((state) => ({
        roleList: [...state.roleList, { name: roleName, voice_id: voiceId }],
        isRoleListLoading: false
      }));
    } catch (error) {
      set({
        roleListError: error instanceof Error ? error.message : 'Failed to add role',
        isRoleListLoading: false
      });
    }
  },

  // Delete role
  deleteRole: async (roleName) => {
    set({ isRoleListLoading: true, roleListError: null });
    try {
      await deleteRole(roleName);
      set((state) => ({
        roleList: state.roleList.filter(r => r.name !== roleName),
        isRoleListLoading: false
      }));
    } catch (error) {
      set({
        roleListError: error instanceof Error ? error.message : 'Failed to delete role',
        isRoleListLoading: false
      });
    }
  },

  // Rename role
  renameRole: async (oldName, newName) => {
    set({ isRoleListLoading: true, roleListError: null });
    try {
      await renameRole(oldName, newName);
      set((state) => ({
        roleList: state.roleList.map(r =>
          r.name === oldName ? { ...r, name: newName } : r
        ),
        isRoleListLoading: false
      }));
    } catch (error) {
      set({
        roleListError: error instanceof Error ? error.message : 'Failed to rename role',
        isRoleListLoading: false
      });
    }
  },

  // Update role voice
  updateRoleVoice: async (roleName, voiceId) => {
    set({ isRoleListLoading: true, roleListError: null });
    try {
      await updateRoleVoice(roleName, voiceId);
      set((state) => ({
        roleList: state.roleList.map(r =>
          r.name === roleName ? { ...r, voice_id: voiceId } : r
        ),
        isRoleListLoading: false
      }));
    } catch (error) {
      set({
        roleListError: error instanceof Error ? error.message : 'Failed to update role voice',
        isRoleListLoading: false
      });
    }
  },

  // Get all groups
  fetchGroups: async () => {
    set({ isGroupsLoading: true, groupsError: null });
    try {
      const data = await getAllGroups();
      set({ groups: data.groups, isGroupsLoading: false });
    } catch (error) {
      set({
        groupsError: error instanceof Error ? error.message : 'Failed to get voice groups',
        isGroupsLoading: false
      });
    }
  },

  // Add group
  addGroup: async (group) => {
    set({ isGroupsLoading: true, groupsError: null });
    try {
      await addGroup(group);
      set((state) => ({
        groups: [...state.groups, group],
        isGroupsLoading: false
      }));
    } catch (error) {
      set({
        groupsError: error instanceof Error ? error.message : 'Failed to add voice group',
        isGroupsLoading: false
      });
    }
  },

  // Update group
  updateGroup: async (groupName, updates) => {
    set({ isGroupsLoading: true, groupsError: null });
    try {
      await updateGroup(groupName, updates);
      set((state) => ({
        groups: state.groups.map(g =>
          g.name === groupName ? { ...g, ...updates } : g
        ),
        isGroupsLoading: false
      }));
    } catch (error) {
      set({
        groupsError: error instanceof Error ? error.message : 'Failed to update voice group',
        isGroupsLoading: false
      });
    }
  },

  // Delete group
  deleteGroup: async (groupName) => {
    set({ isGroupsLoading: true, groupsError: null });
    try {
      await deleteGroup(groupName);
      set((state) => ({
        groups: state.groups.filter(g => g.name !== groupName),
        isGroupsLoading: false
      }));
    } catch (error) {
      set({
        groupsError: error instanceof Error ? error.message : 'Failed to delete voice group',
        isGroupsLoading: false
      });
    }
  },

  // Get current group
  fetchCurrentGroup: async () => {
    set({ isCurrentGroupLoading: true, currentGroupError: null });
    try {
      const data = await getCurrentGroup();
      set({ currentGroup: data.current_group, isCurrentGroupLoading: false });
    } catch (error) {
      set({
        currentGroupError: error instanceof Error ? error.message : 'Failed to get current group',
        isCurrentGroupLoading: false
      });
    }
  },

  // Set current group
  setCurrentGroup: async (groupName) => {
    set({ isCurrentGroupLoading: true, currentGroupError: null });
    try {
      await setCurrentGroup(groupName);
      set({ currentGroup: groupName, isCurrentGroupLoading: false });
    } catch (error) {
      set({
        currentGroupError: error instanceof Error ? error.message : 'Failed to set current group',
        isCurrentGroupLoading: false
      });
    }
  }
}));
