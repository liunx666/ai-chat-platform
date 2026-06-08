<template>
  <div class="admin-layout" :class="{ light: !isDark }">
    <div class="admin-sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-header">
        <span v-if="!sidebarCollapsed">管理后台</span>
        <i class="el-icon-s-management" v-else></i>
      </div>

      <el-menu
        :default-active="activeMenu"
        class="admin-menu"
        :mode="'vertical'"
        :background-color="isDark ? '#1a1a1a' : '#ffffff'"
        :text-color="isDark ? '#cccccc' : '#606266'"
        :active-text-color="isDark ? '#ffffff' : '#409eff'"
        @select="handleMenuSelect"
      >
        <el-menu-item index="/admin">
          <i class="el-icon-data-analysis"></i>
          <span slot="title">数据统计</span>
        </el-menu-item>
        <el-menu-item index="/admin/users">
          <i class="el-icon-user"></i>
          <span slot="title">用户管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/conversations">
          <i class="el-icon-chat-dot-round"></i>
          <span slot="title">对话管理</span>
        </el-menu-item>
      </el-menu>

      <div class="sidebar-footer">
        <el-switch v-model="isDark" active-text="" inactive-text="" @change="toggleTheme"></el-switch>
        <el-button size="small" @click="goChat">返回聊天</el-button>
        <el-button size="small" type="danger" @click="handleLogout">退出登录</el-button>
      </div>
    </div>

    <div class="admin-main">
      <div class="admin-header">
        <div class="header-left">
          <i class="el-icon-s-fold mobile-menu" @click="sidebarCollapsed = !sidebarCollapsed"></i>
          <h2>{{ pageTitle }}</h2>
        </div>
        <div class="header-right">
          <el-dropdown trigger="click" @command="handleCommand">
            <div class="user-info">
              <div class="user-avatar">{{ userInitial }}</div>
              <span class="user-name">{{ username }}</span>
              <el-tag size="mini" type="danger">管理员</el-tag>
              <i class="el-icon-arrow-down"></i>
            </div>
            <el-dropdown-menu slot="dropdown">
              <el-dropdown-item command="password">修改密码</el-dropdown-item>
              <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </el-dropdown>
        </div>
      </div>
      <div class="admin-content">
        <router-view></router-view>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * @file 管理员布局组件
 * @description 管理后台通用布局，包含侧边栏和内容区
 * @author aichat_upend
 */

import { auth } from '@/api';
import { showSuccess } from '@/utils';

export default {
  name: 'AdminLayout',

  data() {
    return {
      activeMenu: '/admin',
      sidebarCollapsed: false
    };
  },

  computed: {
    isDark() {
      return this.$store.getters.isDark;
    },
    username() {
      const user = this.$store.getters.currentUser;
      return user.username || '管理员';
    },
    userInitial() {
      return this.username.charAt(0).toUpperCase();
    },
    pageTitle() {
      const titles = {
        '/admin': '数据统计',
        '/admin/users': '用户管理',
        '/admin/conversations': '对话管理'
      };
      return titles[this.$route.path] || '管理后台';
    }
  },

  watch: {
    $route(to) {
      this.activeMenu = to.path;
    }
  },

  mounted() {
    this.activeMenu = this.$route.path;
  },

  methods: {
    handleMenuSelect(index) {
      if (this.$route.path !== index) {
        this.$router.push(index);
      }
    },

    toggleTheme() {
      this.$store.dispatch('toggleTheme');
    },

    handleCommand(cmd) {
      if (cmd === 'password') {
        this.$router.push('/password');
      } else if (cmd === 'logout') {
        this.handleLogout();
      }
    },

    goChat() {
      this.$router.push('/chat');
    },

    async handleLogout() {
      try {
        await auth.logout();
      } catch {}
      this.$store.dispatch('logout');
      showSuccess('已退出登录');
      this.$router.push('/login');
    }
  }
};
</script>

<style scoped>
.admin-layout {
  display: flex;
  height: 100vh;
  background: #0f0f0f;
  color: #fff;
}
.admin-layout.light {
  background: #f0f2f5;
  color: #1f1f1f;
}

.admin-sidebar {
  width: 220px;
  background: #1a1a1a;
  border-right: 1px solid #333;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  transition: width 0.3s;
}
.admin-sidebar.collapsed {
  width: 64px;
}
.admin-layout.light .admin-sidebar {
  background: #fff;
  border-color: #e5e5e5;
}

.sidebar-header {
  padding: 16px;
  font-size: 16px;
  font-weight: 600;
  border-bottom: 1px solid #333;
  text-align: center;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
.admin-layout.light .sidebar-header {
  border-color: #e5e5e5;
}
.sidebar-header i {
  font-size: 20px;
}

.admin-menu {
  flex: 1;
  border: none !important;
}
.admin-menu >>> .el-menu-item {
  height: 50px;
  line-height: 50px;
}
.admin-menu >>> .el-menu-item i {
  margin-right: 8px;
}

.sidebar-footer {
  padding: 12px;
  border-top: 1px solid #333;
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: center;
}
.admin-layout.light .sidebar-footer {
  border-color: #e5e5e5;
}

.admin-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  height: 56px;
  border-bottom: 1px solid #333;
  background: #1a1a1a;
  flex-shrink: 0;
}
.admin-layout.light .admin-header {
  background: #fff;
  border-color: #e5e5e5;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.header-left h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
}
.mobile-menu {
  font-size: 22px;
  cursor: pointer;
  display: none;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 24px;
  transition: background 0.2s;
}
.user-info:hover {
  background: #2a2a2a;
}
.admin-layout.light .user-info:hover {
  background: #f0f0f0;
}
.user-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 13px;
  color: #fff;
}
.user-name {
  font-size: 14px;
}

.admin-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #0f0f0f;
}
.admin-layout.light .admin-content {
  background: #f0f2f5;
}

@media (max-width: 768px) {
  .admin-sidebar {
    position: fixed;
    top: 0;
    left: -240px;
    z-index: 1000;
    height: 100vh;
    transition: left 0.3s;
    width: 240px !important;
  }
  .admin-sidebar:not(.collapsed) {
    left: 0;
    box-shadow: 4px 0 20px rgba(0, 0, 0, 0.5);
  }
  .mobile-menu {
    display: block;
  }
  .admin-content {
    padding: 16px;
  }
}
</style>
