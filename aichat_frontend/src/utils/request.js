/**
 * @file Axios 请求封装工具
 * @description 封装 Axios 实例，提供请求/响应拦截器，支持环境配置
 * @author aichat_upend
 */

import axios from 'axios';

/**
 * 环境配置
 * @description 根据不同环境配置 API 地址
 */
const ENV_CONFIG = {
  development: {
    baseURL: 'http://127.0.0.1:8000/api'
  },
  production: {
    baseURL: 'http://59.110.233.246:8000/api'
  }
};


/**
 * 超时时间配置（毫秒）
 * @description 普通接口 5 秒，聊天流接口无限制
 */
const TIMEOUT = {
  NORMAL: 5000,    // 普通接口 5 秒
  INFINITE: 0      // 流式接口 无限制
};

/**
 * 获取当前环境
 * @returns {string} 环境名称
 */
const getEnv = () => {
  return process.env.NODE_ENV || 'development';
};

/**
 * 创建 Axios 实例（普通接口）
 * @description 包含请求/响应拦截器，超时 5 秒
 */
const createRequestInstance = () => {
  const instance = axios.create({
    baseURL: ENV_CONFIG[getEnv()].baseURL,
    timeout: TIMEOUT.NORMAL,
    headers: {
      'Content-Type': 'application/json'
    }
  });

  // 请求拦截器
  instance.interceptors.request.use(
    config => {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    error => {
      console.error('[Request Error]:', error);
      return Promise.reject(error);
    }
  );

  // 响应拦截器
  instance.interceptors.response.use(
    response => {
      const res = response.data;
      console.log('[Request Response]:', res);
      
      // 兼容多种响应格式
      // 格式1: { code, message, data }
      // 格式2: { success, data }
      // 格式3: 直接返回数据
      
      // 如果是标准格式且有code字段
      if (res.code !== undefined) {
        if (res.code !== 200 && res.code !== 0) {
          console.error('[Response Error]:', res.message || '请求失败');
          return Promise.reject(new Error(res.message || '请求失败'));
        }
        // 返回包含data的对象，方便前端统一处理
        return res;
      }
      
      // 如果是success格式
      if (res.success !== undefined) {
        if (!res.success) {
          console.error('[Response Error]:', res.message || '请求失败');
          return Promise.reject(new Error(res.message || '请求失败'));
        }
        return res;
      }
      
      // 如果直接返回数据，包装成标准格式
      return { code: 200, data: res };
    },
    error => {
      console.error('[Response Error]:', error);
      if (error.response && error.response.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
      return Promise.reject(error);
    }
  );

  return instance;
};

/**
 * 创建 Axios 实例（流式接口）
 * @description 无超时限制，用于聊天流式请求
 */
const createStreamInstance = () => {
  const instance = axios.create({
    baseURL: ENV_CONFIG[getEnv()].baseURL,
    timeout: TIMEOUT.INFINITE,
    headers: {
      'Content-Type': 'application/json'
    }
  });

  // 流式接口请求拦截器
  instance.interceptors.request.use(
    config => {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    error => {
      console.error('[Request Error]:', error);
      return Promise.reject(error);
    }
  );

  return instance;
};

/**
 * 导出请求实例
 */
export const request = createRequestInstance();
export const streamRequest = createStreamInstance();

/**
 * 导出配置常量供外部使用
 */
export { TIMEOUT, ENV_CONFIG };
