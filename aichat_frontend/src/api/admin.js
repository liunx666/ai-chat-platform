/**
 * @file 管理员接口
 * @description 封装管理员相关的所有接口
 * @author aichat_upend
 */

import { request } from '@/utils/request';

/**
 * 获取所有用户列表
 * @param {Object} params - 查询参数
 * @param {number} [params.page=1] - 页码
 * @param {number} [params.page_size=20] - 每页数量
 * @returns {Promise} 请求 Promise
 * @returns {Array} items - 用户列表
 * @returns {number} items[].id - 用户ID
 * @returns {string} items[].username - 用户名
 * @returns {string} items[].tenant_id - 租户ID
 * @returns {string} items[].role - 角色(admin/user)
 * @returns {number} items[].conversation_count - 对话数量
 * @returns {string} items[].created_at - 创建时间
 */
export function getUsers(params) {
  return request.get('/admin/users', { params });
}

/**
 * 获取单个用户详情
 * @param {number} userId - 用户ID
 * @returns {Promise} 请求 Promise
 * @returns {Object} data - 用户详情
 * @returns {number} data.id - 用户ID
 * @returns {string} data.username - 用户名
 * @returns {string} data.tenant_id - 租户ID
 * @returns {string} data.role - 角色
 * @returns {string} data.created_at - 创建时间
 * @returns {Object} data.statistics - 用户统计
 * @returns {number} data.statistics.total_conversations - 总对话数
 * @returns {number} data.statistics.active_conversations - 活跃对话数
 * @returns {number} data.statistics.deleted_conversations - 已删除对话数
 * @returns {number} data.statistics.total_messages - 总消息数
 * @returns {number} data.statistics.total_tokens - 总Token数
 */
export function getUserDetail(userId) {
  return request.get(`/admin/users/${userId}`);
}

/**
 * 修改用户角色
 * @param {number} userId - 用户ID
 * @param {Object} data - 角色数据
 * @param {string} data.role - 角色：admin 或 user
 * @returns {Promise} 请求 Promise
 * @returns {number} data.id - 用户ID
 * @returns {string} data.username - 用户名
 * @returns {string} data.role - 新角色
 */
export function updateUserRole(userId, data) {
  return request.put(`/admin/users/${userId}/role`, data);
}

/**
 * 获取所有对话列表
 * @param {Object} params - 查询参数
 * @param {number} [params.page=1] - 页码
 * @param {number} [params.page_size=20] - 每页数量
 * @param {number} [params.user_id] - 筛选指定用户的对话
 * @param {boolean} [params.include_deleted=true] - 是否包含软删除
 * @returns {Promise} 请求 Promise
 * @returns {Array} items - 对话列表
 * @returns {number} items[].id - 对话ID
 * @returns {string} items[].tenant_id - 租户ID
 * @returns {number} items[].user_id - 用户ID
 * @returns {string} items[].username - 用户名
 * @returns {string} items[].title - 对话标题
 * @returns {boolean} items[].is_deleted - 是否已删除
 * @returns {number} items[].message_count - 消息数量
 * @returns {string} items[].created_at - 创建时间
 * @returns {string} items[].updated_at - 更新时间
 */
export function getConversations(params) {
  return request.get('/admin/conversations', { params });
}

/**
 * 获取对话详情和所有消息
 * @param {number} conversationId - 对话ID
 * @returns {Promise} 请求 Promise
 * @returns {Object} data - 对话详情
 * @returns {Object} data.conversation - 对话信息
 * @returns {number} data.conversation.id - 对话ID
 * @returns {string} data.conversation.title - 对话标题
 * @returns {number} data.conversation.user_id - 用户ID
 * @returns {string} data.conversation.username - 用户名
 * @returns {boolean} data.conversation.is_deleted - 是否已删除
 * @returns {string} data.conversation.created_at - 创建时间
 * @returns {string} data.conversation.updated_at - 更新时间
 * @returns {Array} data.messages - 消息列表
 * @returns {number} data.messages[].id - 消息ID
 * @returns {string} data.messages[].user_question - 用户问题
 * @returns {string} data.messages[].ai_response - AI回复
 * @returns {string} data.messages[].thinking_content - 深度思考内容
 * @returns {number} data.messages[].token_count - Token数量
 * @returns {string} data.messages[].model - 使用的模型
 * @returns {string} data.messages[].created_at - 创建时间
 * @returns {string} data.messages[].responded_at - 回复时间
 * @returns {Object} data.statistics - 对话统计
 * @returns {number} data.statistics.total_messages - 总消息数
 * @returns {number} data.statistics.ai_responses - AI回复数
 * @returns {number} data.statistics.total_tokens - 总Token数
 */
export function getConversationDetail(conversationId) {
  return request.get(`/admin/conversations/${conversationId}`);
}

/**
 * 强制删除对话
 * @param {number} conversationId - 对话ID
 * @returns {Promise} 请求 Promise
 * @returns {number} data.deleted_conversation_id - 被删除的对话ID
 * @returns {number} data.deleted_messages - 被删除的消息数
 */
export function deleteConversation(conversationId) {
  return request.delete(`/admin/conversations/${conversationId}`);
}

/**
 * 恢复软删除的对话
 * @param {number} conversationId - 对话ID
 * @returns {Promise} 请求 Promise
 * @returns {number} data.id - 对话ID
 * @returns {string} data.title - 对话标题
 * @returns {boolean} data.is_deleted - 是否已删除(恢复后为false)
 */
export function restoreConversation(conversationId) {
  return request.post(`/admin/conversations/${conversationId}/restore`);
}

/**
 * 获取系统统计信息
 * @returns {Promise} 请求 Promise
 * @returns {Object} data - 统计数据
 * @returns {Object} data.users - 用户统计
 * @returns {number} data.users.total - 用户总数
 * @returns {number} data.users.admins - 管理员数量
 * @returns {number} data.users.normal_users - 普通用户数量
 * @returns {Object} data.conversations - 对话统计
 * @returns {number} data.conversations.total - 对话总数
 * @returns {number} data.conversations.active - 活跃对话数
 * @returns {number} data.conversations.deleted - 已删除对话数
 * @returns {Object} data.messages - 消息统计
 * @returns {number} data.messages.total - 消息总数
 * @returns {number} data.messages.ai_responses - AI回复数
 * @returns {number} data.messages.pending - 待处理数
 * @returns {Object} data.tokens - Token统计
 * @returns {number} data.tokens.total - Token总数
 */
export function getStatistics() {
  return request.get('/admin/statistics');
}
