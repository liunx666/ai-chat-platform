/**
 * @file 用户认证接口
 * @description 封装用户注册、登录、登出、修改密码等接口
 * @author aichat_upend
 */

import { request } from '@/utils/request';

/**
 * 用户注册
 * @param {Object} data - 注册数据
 * @param {string} data.username - 用户名
 * @param {string} data.password - 密码
 * @returns {Promise} 请求 Promise
 */
export function register(data) {
  return request.post('/user/register', data);
}

/**
 * 用户登录
 * @param {Object} data - 登录数据
 * @param {string} data.username - 用户名
 * @param {string} data.password - 密码
 * @returns {Promise} 请求 Promise
 */
export function login(data) {
  return request.post('/user/login', data);
}

/**
 * 用户登出
 * @returns {Promise} 请求 Promise
 */
export function logout() {
  return request.post('/user/logout');
}

/**
 * 修改密码
 * @param {Object} data - 密码数据
 * @param {string} data.old_password - 旧密码
 * @param {string} data.new_password - 新密码
 * @returns {Promise} 请求 Promise
 */
export function updatePassword(data) {
  return request.put('/user/password', data);
}
