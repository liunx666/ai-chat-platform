<template>
  <div class="admin-dashboard" :class="{ light: !isDark }">
    <el-row :gutter="20">
      <el-col :xs="24" :sm="12" :md="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: #409EFF;">
            <i class="el-icon-user"></i>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.users?.total || 0 }}</div>
            <div class="stat-label">用户总数</div>
            <div class="stat-detail">
              <span>管理员 {{ stats.users?.admins || 0 }}</span> /
              <span>普通 {{ stats.users?.normal_users || 0 }}</span>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: #67C23A;">
            <i class="el-icon-chat-dot-round"></i>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.conversations?.total || 0 }}</div>
            <div class="stat-label">对话总数</div>
            <div class="stat-detail">
              <span>活跃 {{ stats.conversations?.active || 0 }}</span> /
              <span>已删 {{ stats.conversations?.deleted || 0 }}</span>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: #E6A23C;">
            <i class="el-icon-message"></i>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.messages?.total || 0 }}</div>
            <div class="stat-label">消息总数</div>
            <div class="stat-detail">
              <span>AI回复 {{ stats.messages?.ai_responses || 0 }}</span> /
              <span>待处理 {{ stats.messages?.pending || 0 }}</span>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: #F56C6C;">
            <i class="el-icon-coin"></i>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ formatNumber(stats.tokens?.total || 0) }}</div>
            <div class="stat-label">Token总数</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :xs="24" :md="12">
        <div class="chart-card">
          <div class="card-header">
            <h3>最近对话</h3>
            <el-button type="text" size="small" @click="$router.push('/admin/conversations')">查看更多</el-button>
          </div>
          <div class="activity-list" v-loading="loadingActivity">
            <div v-for="item in recentActivity" :key="item.id" class="activity-item" @click="viewConversation(item.id)">
              <div class="activity-content">
                <span class="activity-title">{{ item.title }}</span>
                <span class="activity-user">
                  <i class="el-icon-user"></i> {{ item.username || '未知用户' }}
                  <i class="el-icon-chat-line-round"></i> {{ item.message_count || 0 }} 条消息
                </span>
              </div>
              <div class="activity-time">{{ formatTime(item.created_at) }}</div>
            </div>
            <div v-if="recentActivity.length === 0 && !loadingActivity" class="empty-tip">
              暂无对话记录
            </div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :md="12">
        <div class="chart-card">
          <div class="card-header">
            <h3>系统信息</h3>
          </div>
          <div class="system-info">
            <div class="info-item">
              <span class="info-label">当前租户</span>
              <span class="info-value">{{ tenantId }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">系统版本</span>
              <span class="info-value">v1.0.0</span>
            </div>
            <div class="info-item">
              <span class="info-label">当前用户</span>
              <span class="info-value">{{ username }}</span>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script>
/**
 * @file 管理员数据统计页面
 * @description 展示系统统计数据、对话统计等
 * @author aichat_upend
 */

import { admin } from '@/api';

export default {
  name: 'AdminDashboard',

  data() {
    return {
      loadingActivity: false,
      recentActivity: [],
      stats: {}
    };
  },

  computed: {
    isDark() {
      return this.$store.getters.isDark;
    },
    tenantId() {
      return this.$store.getters.tenantId;
    },
    username() {
      return this.$store.getters.currentUser.username || '管理员';
    }
  },

  mounted() {
    this.loadStatistics();
    this.loadRecentActivity();
  },

  methods: {
    /**
     * 加载统计数据 - 排查点：
     * 1. 检查接口调用是否成功
     * 2. 检查返回数据结构是否正确
     * 3. 检查 res.data 是否存在且包含预期字段
     */
    async loadStatistics() {
      try {
        console.log('[AdminDashboard] 开始加载统计数据...');
        const res = await admin.getStatistics();
        console.log('[AdminDashboard] 统计数据接口返回:', res);
        
        // 排查：检查响应结构
        if (!res || !res.data) {
          console.error('[AdminDashboard] 错误：接口返回为空或没有data字段');
          this.stats = {};
          return;
        }
        
        // 排查：检查数据字段是否存在
        console.log('[AdminDashboard] 统计数据:', res.data);
        console.log('[AdminDashboard] 用户统计:', res.data.users);
        console.log('[AdminDashboard] 对话统计:', res.data.conversations);
        console.log('[AdminDashboard] 消息统计:', res.data.messages);
        console.log('[AdminDashboard] Token统计:', res.data.tokens);
        
        this.stats = res.data || {};
      } catch (error) {
        console.error('[AdminDashboard] 加载统计数据失败:', error);
        console.error('[AdminDashboard] 错误详情:', error.message, error.response);
        this.stats = {};
      }
    },

    /**
     * 加载最近对话活动 - 排查点：
     * 1. 检查接口调用是否成功
     * 2. 检查返回的items数组是否存在
     * 3. 检查每个item的字段是否完整
     */
    async loadRecentActivity() {
      this.loadingActivity = true;
      try {
        console.log('[AdminDashboard] 开始加载最近对话...');
        const res = await admin.getConversations({ page: 1, page_size: 10 });
        console.log('[AdminDashboard] 最近对话接口返回:', res);
        
        // 排查：检查响应结构
        if (!res || !res.data) {
          console.error('[AdminDashboard] 错误：最近对话接口返回为空或没有data字段');
          this.recentActivity = [];
          return;
        }
        
        // 排查：检查items数组
        const items = res.data.items || [];
        console.log('[AdminDashboard] 对话列表长度:', items.length);
        console.log('[AdminDashboard] 对话列表数据:', items);
        
        this.recentActivity = items.map((item, index) => {
          console.log(`[AdminDashboard] 对话${index}: id=${item.id}, title=${item.title}, username=${item.username}`);
          return {
            id: item.id,
            title: item.title || '无标题',
            username: item.username,
            message_count: item.message_count,
            created_at: item.created_at
          };
        });
      } catch (error) {
        console.error('[AdminDashboard] 加载最近对话失败:', error);
        console.error('[AdminDashboard] 错误详情:', error.message, error.response);
        this.recentActivity = [];
      } finally {
        this.loadingActivity = false;
      }
    },

    viewConversation(id) {
      this.$router.push(`/admin/conversations`);
    },

    formatTime(time) {
      if (!time) return '-';
      const date = new Date(time);
      return date.toLocaleDateString('zh-CN', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
    },

    formatNumber(num) {
      if (num >= 10000) {
        return (num / 10000).toFixed(1) + 'w';
      }
      return num.toString();
    }
  }
};
</script>

<style scoped>
.admin-dashboard { padding: 0; }

.stat-card {
  background: #2a2a2a;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}
.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}
.light .stat-card {
  background: #fff;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #fff;
}

.stat-info { flex: 1; }
.stat-value { font-size: 28px; font-weight: 600; margin-bottom: 4px; }
.stat-label { font-size: 13px; opacity: 0.7; margin-bottom: 4px; }
.stat-detail { font-size: 12px; opacity: 0.5; }

.chart-card {
  background: #2a2a2a;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
}
.light .chart-card {
  background: #fff;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.card-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
}

.activity-list { min-height: 200px; }
.activity-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
  margin-bottom: 8px;
  background: #333;
}
.activity-item:hover {
  background: #444;
}
.light .activity-item {
  background: #f5f5f5;
}
.light .activity-item:hover {
  background: #e5e5e5;
}

.activity-content { display: flex; flex-direction: column; gap: 4px; }
.activity-title { font-weight: 500; }
.activity-user { font-size: 12px; opacity: 0.6; display: flex; gap: 8px; }
.activity-time { font-size: 12px; opacity: 0.6; white-space: nowrap; }
.empty-tip { text-align: center; padding: 40px 0; opacity: 0.6; font-size: 14px; }

.system-info { display: flex; flex-direction: column; }
.info-item {
  display: flex;
  justify-content: space-between;
  padding: 14px 0;
  border-bottom: 1px solid #333;
}
.light .info-item { border-color: #f0f0f0; }
.info-item:last-child { border-bottom: none; }
.info-label { opacity: 0.7; }
.info-value { font-weight: 500; }
</style>
