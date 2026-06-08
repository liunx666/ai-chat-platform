<template>
  <div class="password-page">
    <div class="password-card">
      <h2 class="password-title">修改密码</h2>
      
      <el-input
        v-model="form.oldPassword"
        type="password"
        placeholder="请输入旧密码"
        class="password-input"
        prefix-icon="el-icon-lock"
        show-password
        clearable
      ></el-input>
      
      <el-input
        v-model="form.newPassword"
        type="password"
        placeholder="请输入新密码"
        class="password-input"
        prefix-icon="el-icon-unlock"
        show-password
        clearable
      ></el-input>
      
      <el-input
        v-model="form.confirmPassword"
        type="password"
        placeholder="请再次输入新密码"
        class="password-input"
        prefix-icon="el-icon-check"
        show-password
        clearable
      ></el-input>
      
      <el-button
        type="primary"
        class="password-button"
        :loading="loading"
        @click="handleSubmit"
      >
        {{ loading ? '提交中...' : '确认修改' }}
      </el-button>
      
      <el-button
        class="cancel-button"
        @click="goBack"
      >
        取消
      </el-button>
    </div>
  </div>
</template>

<script>
/**
 * @file 修改密码页面组件
 * @description 提供用户修改密码功能
 * @author aichat_upend
 */

import { auth } from '@/api';
import {
  validatePassword,
  validateNewPassword,
  validateConfirmPassword
} from '@/utils/validate';
import { showSuccess, showError, showWarning } from '@/utils';

export default {
  name: 'Password',

  /**
   * 组件数据
   */
  data() {
    return {
      loading: false, // 提交加载状态
      form: {
        oldPassword: '',    // 旧密码
        newPassword: '',    // 新密码
        confirmPassword: '' // 确认密码
      }
    };
  },

  /**
   * 组件方法
   */
  methods: {
    /**
     * 返回上一页
     */
    goBack() {
      this.$router.push('/chat');
    },

    /**
     * 处理修改密码提交
     */
    async handleSubmit() {
      // 表单验证
      const oldValid = validatePassword(this.form.oldPassword);
      if (oldValid !== true) {
        showWarning(oldValid);
        return;
      }
      
      const newValid = validateNewPassword(this.form.newPassword, this.form.oldPassword);
      if (newValid !== true) {
        showWarning(newValid);
        return;
      }
      
      const confirmValid = validateConfirmPassword(this.form.confirmPassword, this.form.newPassword);
      if (confirmValid !== true) {
        showWarning(confirmValid);
        return;
      }

      this.loading = true;

      try {
        await auth.updatePassword({
          old_password: this.form.oldPassword,
          new_password: this.form.newPassword
        });
        
        showSuccess('密码修改成功');
        
        // 跳转到聊天页面
        this.$router.push('/chat');
      } catch (error) {
        showError(error.message || '密码修改失败，请检查旧密码是否正确');
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
/**
 * 修改密码页面样式
 */
.password-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
}

.password-card {
  width: 360px;
  padding: 48px 40px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  transition: transform 0.3s, box-shadow 0.3s;
}

.password-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.18);
}

.password-title {
  text-align: center;
  margin: 0 0 32px;
  color: #333;
  font-size: 24px;
  font-weight: 600;
}

.password-input {
  margin-bottom: 20px;
}

.password-button {
  width: 100%;
  padding: 12px 20px;
  font-size: 16px;
  border-radius: 6px;
  margin-bottom: 12px;
}

.cancel-button {
  width: 100%;
  padding: 10px 20px;
  border-radius: 6px;
}
</style>
