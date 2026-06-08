/**
 * @file 表单验证工具类
 * @description 提供常用的表单验证规则
 * @author aichat_upend
 */

/**
 * 用户名验证规则
 * @param {string} value - 用户名
 * @returns {boolean|string} 验证通过返回true，失败返回错误信息
 */
export const validateUsername = (value) => {
  if (!value) {
    return '请输入用户名';
  }
  if (value.length < 3) {
    return '用户名至少需要3个字符';
  }
  if (value.length > 20) {
    return '用户名最多20个字符';
  }
  return true;
};

/**
 * 密码验证规则
 * @param {string} value - 密码
 * @returns {boolean|string} 验证通过返回true，失败返回错误信息
 */
export const validatePassword = (value) => {
  if (!value) {
    return '请输入密码';
  }
  if (value.length < 6) {
    return '密码至少需要6个字符';
  }
  if (value.length > 32) {
    return '密码最多32个字符';
  }
  return true;
};

/**
 * 新密码验证规则
 * @param {string} value - 新密码
 * @param {string} oldPassword - 旧密码
 * @returns {boolean|string} 验证通过返回true，失败返回错误信息
 */
export const validateNewPassword = (value, oldPassword) => {
  const result = validatePassword(value);
  if (result !== true) {
    return result;
  }
  if (value === oldPassword) {
    return '新密码不能与旧密码相同';
  }
  return true;
};

/**
 * 确认密码验证规则
 * @param {string} value - 确认密码
 * @param {string} newPassword - 新密码
 * @returns {boolean|string} 验证通过返回true，失败返回错误信息
 */
export const validateConfirmPassword = (value, newPassword) => {
  if (!value) {
    return '请确认密码';
  }
  if (value !== newPassword) {
    return '两次输入的密码不一致';
  }
  return true;
};

/**
 * 问题内容验证规则
 * @param {string} value - 问题内容
 * @returns {boolean|string} 验证通过返回true，失败返回错误信息
 */
export const validateQuestion = (value) => {
  if (!value || !value.trim()) {
    return '请输入问题内容';
  }
  if (value.trim().length > 2000) {
    return '问题内容不能超过2000个字符';
  }
  return true;
};
