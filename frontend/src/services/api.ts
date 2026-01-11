import axios from 'axios';

// 根据环境变量获取API基础URL
const getApiBaseUrl = () => {
  // 检查是否在Docker环境中
  if (import.meta.env.VITE_DOCKER === '1') {
    // Docker部署模式：使用相对路径，由nginx代理到后端
    return '/api';
  }
  // 开发模式：直接连接后端API
  return 'http://localhost:8000/api';
};

// 创建axios实例
const api = axios.create({
  baseURL: getApiBaseUrl(), // 根据环境动态设置
  timeout: 600000, // 请求超时时间
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证信息等
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    // 如果响应类型是blob，直接返回整个响应对象
    if (response.config.responseType === 'blob') {
      return response;
    }
    // 否则返回响应数据
    return response.data;
  },
  (error) => {
    console.error('API请求错误:', error);
    return Promise.reject(error);
  }
);

export default api;
