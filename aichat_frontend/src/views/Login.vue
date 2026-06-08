<template>
  <div class="login-page">
    <div class="login-card">
      <h2 class="login-title">登录</h2>
      
      <el-input
        v-model="form.username"
        placeholder="请输入账号"
        class="login-input"
        prefix-icon="el-icon-user"
        clearable
        @keyup.enter.native="handleLogin"
      ></el-input>
      
      <el-input
        v-model="form.password"
        type="password"
        placeholder="请输入密码"
        class="login-input"
        prefix-icon="el-icon-lock"
        show-password
        clearable
        @keyup.enter.native="handleLogin"
      ></el-input>
      
      <el-button
        type="primary"
        class="login-button"
        :loading="loading"
        @click="handleLogin"
      >
        {{ loading ? '登录中...' : '登录' }}
      </el-button>
      
      <div class="login-footer">
        <span>没有账号？</span>
        <router-link to="/register" class="register-link">立即注册</router-link>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * @file 登录页面组件
 * @description 提供用户登录功能，支持账号密码登录
 * @author aichat_upend
 */

import { auth } from '@/api';
import { validateUsername, validatePassword } from '@/utils/validate';
import { showSuccess, showError, showWarning } from '@/utils';

export default {
  name: 'Login',

  /**
   * 组件数据
   */
  data() {
    return {
      loading: false, // 登录加载状态
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
     * 处理登录操作
     */
    async handleLogin() {
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
        const res = await auth.login(this.form);

        this.$store.dispatch('login', {
          token: res.data.token,
          user: res.data.userInfo
        });

        showSuccess('登录成功');

        const role = res.data.userInfo.role;
        if (role === 'admin') {
          this.$router.push('/admin');
        } else {
          this.$router.push('/chat');
        }
      } catch (error) {
        showError(error.message || '登录失败，请检查账号密码');
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
/**
 * 登录页面样式
 */
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
}

.login-card {
  width: 360px;
  padding: 48px 40px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  transition: transform 0.3s, box-shadow 0.3s;
}

.login-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.18);
}

.login-title {
  text-align: center;
  margin: 0 0 32px;
  color: #333;
  font-size: 24px;
  font-weight: 600;
}

.login-input {
  margin-bottom: 20px;
}

.login-button {
  width: 100%;
  padding: 12px 20px;
  font-size: 16px;
  border-radius: 6px;
}

.login-footer {
  text-align: center;
  font-size: 14px;
  color: #666;
  margin-top: 24px;
}

.register-link {
  color: #409eff;
  text-decoration: none;
  margin-left: 4px;
  font-weight: 500;
  transition: color 0.2s;
}

.register-link:hover {
  color: #66b1ff;
  text-decoration: underline;
}
</style>
