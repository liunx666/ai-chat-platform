<template>
  <div class="register-page">
    <div class="register-card">
      <h2 class="register-title">注册</h2>
      
      <el-input
        v-model="form.username"
        placeholder="请输入账号"
        class="register-input"
        prefix-icon="el-icon-user"
        clearable
        @keyup.enter.native="handleRegister"
      ></el-input>
      
      <el-input
        v-model="form.password"
        type="password"
        placeholder="请输入密码"
        class="register-input"
        prefix-icon="el-icon-lock"
        show-password
        clearable
        @keyup.enter.native="handleRegister"
      ></el-input>
      
      <el-button
        type="primary"
        class="register-button"
        :loading="loading"
        @click="handleRegister"
      >
        {{ loading ? '注册中...' : '注册' }}
      </el-button>
      
      <div class="register-footer">
        <span>已有账号？</span>
        <router-link to="/login" class="login-link">立即登录</router-link>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * @file 注册页面组件
 * @description 提供用户注册功能，支持账号密码注册
 * @author aichat_upend
 */

import { auth } from '@/api';
import { validateUsername, validatePassword } from '@/utils/validate';
import { showSuccess, showError, showWarning } from '@/utils';

export default {
  name: 'Register',

  /**
   * 组件数据
   */
  data() {
    return {
      loading: false, // 注册加载状态
      form: {
        username: '', // 用户名
        password: ''  // 密码
      }
    };
  },

  /**
   * 组件方法
   */
  methods: {
    /**
     * 处理注册操作
     */
    async handleRegister() {
      // 表单验证
      const usernameValid = validateUsername(this.form.username);
      if (usernameValid !== true) {
        showWarning(usernameValid);
        return;
      }
      
      const passwordValid = validatePassword(this.form.password);
      if (passwordValid !== true) {
        showWarning(passwordValid);
        return;
      }

      this.loading = true;

      try {
        await auth.register(this.form);
        showSuccess('注册成功，请登录');
        
        // 跳转到登录页面
        this.$router.push('/login');
      } catch (error) {
        showError(error.message || '注册失败，请稍后重试');
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
/**
 * 注册页面样式
 */
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
}

.register-card {
  width: 360px;
  padding: 48px 40px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  transition: transform 0.3s, box-shadow 0.3s;
}

.register-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.18);
}

.register-title {
  text-align: center;
  margin: 0 0 32px;
  color: #333;
  font-size: 24px;
  font-weight: 600;
}

.register-input {
  margin-bottom: 20px;
}

.register-button {
  width: 100%;
  padding: 12px 20px;
  font-size: 16px;
  border-radius: 6px;
}

.register-footer {
  text-align: center;
  font-size: 14px;
  color: #666;
  margin-top: 24px;
}

.login-link {
  color: #409eff;
  text-decoration: none;
  margin-left: 4px;
  font-weight: 500;
  transition: color 0.2s;
}

.login-link:hover {
  color: #66b1ff;
  text-decoration: underline;
}
</style>
