/**
 * @file 对话管理接口
 * @description 封装用户对话的创建、查询、更新、删除等接口
 * @author aichat_upend
 */

import { request } from '@/utils/request';

/**
 * 创建新对话
 * @param {Object} data - 对话数据
 * @param {string} [data.title] - 对话标题
 * @returns {Promise} 请求 Promise
 */
export function create(data) {
  return request.post('/conversation/create', data);
}

/**
 * 获取对话列表（分页）
 * @param {Object} params - 查询参数
 * @param {number} [params.page=1] - 页码
 * @param {number} [params.page_size=20] - 每页数量
 * @returns {Promise} 请求 Promise
 */
export function getList(params) {
  return request.get('/conversation/list', { params }).then(res => {
    console.log('[API Response]: conversation/list', res);
    return res;
  });
}

/**
 * 获取对话详情（含消息）
 * @param {number} id - 对话ID
 * @returns {Promise} 请求 Promise
 */
export function getDetail(id) {
  return request.get(`/conversation/detail/${id}`);
}

/**
 * 更新对话标题
 * @param {number} id - 对话ID
 * @param {Object} data - 更新数据
 * @param {string} data.title - 新标题
 * @returns {Promise} 请求 Promise
 */
export function update(id, data) {
  return request.put(`/conversation/update/${id}`, data);
}

/**
 * 删除对话（软删除）
 * @param {number} id - 对话ID
 * @returns {Promise} 请求 Promise
 */
export function remove(id) {
  return request.delete(`/conversation/delete/${id}`);
}