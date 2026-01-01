import api from './api';
import type {
  GetEnvConfigResponse,
  UpdateEnvConfigRequest,
  UpdateEnvConfigResponse,
  GetRolesConfigResponse,
  UpdateRolesConfigRequest,
  UpdateRolesConfigResponse
} from '../types/config';

// 获取环境变量配置
export const getEnvConfig = async (): Promise<GetEnvConfigResponse> => {
  return api.get('/config/env');
};

// 更新环境变量配置
export const updateEnvConfig = async (config: UpdateEnvConfigRequest): Promise<UpdateEnvConfigResponse> => {
  return api.put('/config/env', config);
};

// 获取角色配置
export const getRoleConfig = async (): Promise<GetRolesConfigResponse> => {
  return api.get('/config/roles');
};

// 更新角色配置
export const updateRoleConfig = async (config: UpdateRolesConfigRequest): Promise<UpdateRolesConfigResponse> => {
  return api.put('/config/roles', config);
};
