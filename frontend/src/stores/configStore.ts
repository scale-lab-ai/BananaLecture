import { create } from 'zustand';
import type { EnvConfig, RoleConfig } from '../types/config';
import { getEnvConfig, getRoleConfig, updateEnvConfig, updateRoleConfig } from '../services/configService';

interface ConfigState {
  // 环境变量配置
  envConfig: EnvConfig;
  isEnvLoading: boolean;
  envError: string | null;
  
  // 角色配置
  roleConfig: RoleConfig;
  isRoleLoading: boolean;
  roleError: string | null;
  
  // 操作方法
  fetchEnvConfig: () => Promise<void>;
  updateEnvConfig: (config: EnvConfig) => Promise<void>;
  fetchRoleConfig: () => Promise<void>;
  updateRoleConfig: (config: RoleConfig) => Promise<void>;
}

// 初始环境配置
const initialEnvConfig: EnvConfig = {
  LLM_OPENAI_API_KEY: '',
  LLM_OPENAI_BASE_URL: '',
  LLM_OPENAI_MODEL: '',
  MINIMAX_AUDIO_API_KEY: '',
  MINIMAX_AUDIO_GROUP_ID: '',
  MINIMAX_AUDIO_MODEL: ''
};

// 初始角色配置
const initialRoleConfig: RoleConfig = {
  '旁白': '',
  '大雄': '',
  '哆啦A梦': '',
  '道具': '',
  '其他男声': '',
  '其他女声': '',
  '其他': ''
};

// 创建配置状态管理
export const useConfigStore = create<ConfigState>((set) => ({
  // 环境变量配置
  envConfig: initialEnvConfig,
  isEnvLoading: false,
  envError: null,
  
  // 角色配置
  roleConfig: initialRoleConfig,
  isRoleLoading: false,
  roleError: null,
  
  // 获取环境变量配置
  fetchEnvConfig: async () => {
    set({ isEnvLoading: true, envError: null });
    try {
      const data = await getEnvConfig();
      set({ envConfig: data, isEnvLoading: false });
    } catch (error) {
      set({ 
        envError: error instanceof Error ? error.message : '获取环境配置失败', 
        isEnvLoading: false 
      });
    }
  },
  
  // 更新环境变量配置
  updateEnvConfig: async (config) => {
    set({ isEnvLoading: true, envError: null });
    try {
      await updateEnvConfig(config);
      set({ envConfig: config, isEnvLoading: false });
    } catch (error) {
      set({ 
        envError: error instanceof Error ? error.message : '更新环境配置失败', 
        isEnvLoading: false 
      });
    }
  },
  
  // 获取角色配置
  fetchRoleConfig: async () => {
    set({ isRoleLoading: true, roleError: null });
    try {
      const data = await getRoleConfig();
      set({ roleConfig: data, isRoleLoading: false });
    } catch (error) {
      set({ 
        roleError: error instanceof Error ? error.message : '获取角色配置失败', 
        isRoleLoading: false 
      });
    }
  },
  
  // 更新角色配置
  updateRoleConfig: async (config) => {
    set({ isRoleLoading: true, roleError: null });
    try {
      await updateRoleConfig(config);
      set({ roleConfig: config, isRoleLoading: false });
    } catch (error) {
      set({ 
        roleError: error instanceof Error ? error.message : '更新角色配置失败', 
        isRoleLoading: false 
      });
    }
  }
}));
