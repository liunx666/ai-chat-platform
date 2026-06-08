<template>
  <div class="admin-conversations" :class="{ light: !isDark }">
    <el-card class="filter-card" shadow="never">
      <div class="filter-bar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索对话标题..."
          clearable
          style="width: 200px;"
          @clear="loadConversations"
          @keyup.enter.native="loadConversations"
        >
          <i slot="prefix" class="el-icon-search"></i>
        </el-input>
        <el-select v-model="filterUserId" placeholder="筛选用户" clearable style="width: 150px;" @change="loadConversations">
          <el-option label="全部用户" value=""></el-option>
          <el-option v-for="user in users" :key="user.id" :label="user.username" :value="user.id" />
        </el-select>
        <el-checkbox v-model="includeDeleted" @change="loadConversations">包含已删除</el-checkbox>
        <el-button icon="el-icon-refresh" @click="loadConversations">刷新</el-button>
      </div>
    </el-card>

    <el-card class="table-card" shadow="never">
      <el-table
        :data="tableData"
        v-loading="loading"
        border
        stripe
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" sortable />
        <el-table-column prop="title" label="对话标题" min-width="150" show-overflow-tooltip />
        <el-table-column prop="username" label="用户" width="120" show-overflow-tooltip />
        <el-table-column prop="message_count" label="消息数" width="100" sortable />
        <el-table-column prop="is_deleted" label="状态" width="100">
          <template v-slot="{ row }">
            <el-tag :type="row?.is_deleted ? 'info' : 'success'" size="small">
              {{ row?.is_deleted ? '已删除' : '正常' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template v-slot="{ row }">
            {{ formatTime(row?.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template v-slot="{ row }">
            <el-button type="primary" size="mini" @click="row && viewMessages(row)">查看</el-button>
            <el-button v-if="row?.is_deleted" type="success" size="mini" @click="row && handleRestore(row)">恢复</el-button>
            <el-button v-else type="danger" size="mini" @click="row && handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap">
        <el-pagination
          background
          layout="total, prev, pager, next"
          :current-page="pagination.page"
          :page-size="pagination.page_size"
          :total="pagination.total"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <el-dialog
      v-model:visible="dialogVisible"
      :title="dialogTitle"
      width="75%"
      :fullscreen="isMobile"
      :close-on-click-modal="false"
    >
      <div class="dialog-stats" v-if="conversationStats">
        <span><i class="el-icon-chat-line-round"></i> {{ conversationStats.total_messages || 0 }} 条消息</span>
        <span><i class="el-icon-coffee"></i> {{ conversationStats.ai_responses || 0 }} 次AI回复</span>
        <span><i class="el-icon-coin"></i> {{ conversationStats.total_tokens || 0 }} Tokens</span>
      </div>
      <div class="messages-container" v-loading="loadingMessages">
        <div v-if="messages.length === 0 && !loadingMessages" class="empty-tip">
          暂无消息记录
        </div>
        <div v-for="(msg, index) in messages" :key="index" class="message-item">
          <div class="message-qa">
            <div class="qa-item user">
              <div class="qa-label"><i class="el-icon-user"></i> 用户</div>
              <div class="qa-content">{{ msg.user_question }}</div>
              <div class="qa-time">{{ formatTime(msg.created_at) }}</div>
            </div>
            <div class="qa-item assistant">
              <div class="qa-label"><i class="el-icon-chat-dot-round"></i> AI 回复</div>
              <div class="qa-content">{{ msg.ai_response }}</div>
              <div class="qa-meta">
                <span v-if="msg.thinking_content" class="thinking-indicator">
                  <i class="el-icon-magic-stick"></i> 深度思考
                </span>
                <span v-if="msg.token_count"><i class="el-icon-coin"></i> {{ msg.token_count }} tokens</span>
                <span v-if="msg.model"><i class="el-icon-cpu"></i> {{ msg.model }}</span>
                <span>{{ formatTime(msg.responded_at) }}</span>
              </div>
            </div>
            <div v-if="msg.thinking_content" class="qa-item thinking">
              <div class="qa-label"><i class="el-icon-magic-stick"></i> 深度思考</div>
              <div class="qa-content thinking-content">{{ msg.thinking_content }}</div>
            </div>
          </div>
        </div>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">关闭</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
/**
 * @file 管理员对话管理页面
 * @description 管理所有对话，可以查看对话消息、删除和恢复对话
 * @author aichat_upend
 */

import { admin } from '@/api';
import { showSuccess, showError } from '@/utils';
import { ElMessageBox } from 'element-plus';

export default {
  name: 'AdminConversations',

  data() {
    return {
      loading: false,
      loadingMessages: false,
      searchKeyword: '',
      filterUserId: '',
      includeDeleted: true,
      users: [],
      tableData: [],
      pagination: {
        page: 1,
        page_size: 20,
        total: 0
      },
      dialogVisible: false,
      dialogTitle: '对话详情',
      messages: [],
      conversationStats: null,
      currentConversationId: null
    };
  },

  computed: {
    isDark() {
      return this.$store.getters.isDark;
    },
    isMobile() {
      return window.innerWidth <= 768;
    }
  },

  mounted() {
    this.loadUsers();
    this.loadConversations();
  },

  methods: {
    /**
     * 加载用户列表（用于筛选下拉框）- 排查点：
     * 1. 检查接口调用是否成功
     * 2. 检查返回数据结构是否正确
     */
    async loadUsers() {
      try {
        console.log('[AdminConversations] 开始加载用户列表（筛选用）...');
        const res = await admin.getUsers({ page: 1, page_size: 100 });
        console.log('[AdminConversations] 用户列表接口返回:', res);
        
        // 排查：检查响应结构
        if (!res || !res.data) {
          console.error('[AdminConversations] 错误：用户列表接口返回为空或没有data字段');
          this.users = [];
          return;
        }
        
        this.users = res.data.items || [];
        console.log('[AdminConversations] 用户列表长度:', this.users.length);
      } catch (error) {
        console.error('[AdminConversations] 加载用户列表失败:', error);
        this.users = [];
      }
    },

    /**
     * 加载对话列表 - 排查点：
     * 1. 检查请求参数是否正确
     * 2. 检查接口调用是否成功
     * 3. 检查返回数据结构是否正确（res.data.items 和 res.data.total）
     * 4. 检查每个对话项的字段是否完整
     */
    async loadConversations() {
      this.loading = true;
      try {
        const params = {
          page: this.pagination.page,
          page_size: this.pagination.page_size,
          include_deleted: this.includeDeleted
        };
        if (this.filterUserId) {
          params.user_id = this.filterUserId;
        }
        if (this.searchKeyword) {
          params.keyword = this.searchKeyword;
        }
        
        console.log('[AdminConversations] 开始加载对话列表...');
        console.log('[AdminConversations] 请求参数:', params);
        
        const res = await admin.getConversations(params);
        console.log('[AdminConversations] 对话列表接口返回:', res);
        
        // 排查：检查响应结构
        if (!res || !res.data) {
          console.error('[AdminConversations] 错误：对话列表接口返回为空或没有data字段');
          this.tableData = [];
          this.pagination.total = 0;
          return;
        }
        
        // 排查：检查数据结构
        const items = res.data.items || [];
        const total = res.data.total || 0;
        console.log('[AdminConversations] 对话列表长度:', items.length);
        console.log('[AdminConversations] 对话总数:', total);
        
        // 排查：检查第一个对话的字段
        if (items.length > 0) {
          console.log('[AdminConversations] 第一个对话详情:', {
            id: items[0].id,
            title: items[0].title,
            username: items[0].username,
            message_count: items[0].message_count,
            is_deleted: items[0].is_deleted,
            created_at: items[0].created_at
          });
          
          // 排查：打印数据的所有键名，检查字段名是否匹配
          console.log('[AdminConversations] 第一个对话的所有字段:', Object.keys(items[0]));
        }
        
        // 过滤掉 undefined 和 null 的数据项，避免渲染错误
        const validItems = items.filter(item => item !== undefined && item !== null && typeof item === 'object');
        
        // 字段名转换：将驼峰命名转换为下划线命名，确保与模板prop匹配
        const transformedItems = validItems.map(item => {
          const transformed = {};
          for (const key of Object.keys(item)) {
            // 驼峰转下划线：messageCount -> message_count
            const underscoreKey = key.replace(/([A-Z])/g, '_$1').toLowerCase();
            transformed[underscoreKey] = item[key];
            // 同时保留原始字段，兼容两种命名方式
            transformed[key] = item[key];
          }
          // 确保必要字段存在，避免渲染时出错
          if (transformed.is_deleted === undefined) {
            transformed.is_deleted = false;
          }
          return transformed;
        });
        
        console.log('[AdminConversations] 转换后的对话数据:', transformedItems);
        
        this.tableData = transformedItems;
        this.pagination.total = total;
        
        // 调试：确认数据赋值成功
        console.log('[AdminConversations] 数据赋值完成');
        console.log('[AdminConversations] tableData 长度:', this.tableData.length);
        console.log('[AdminConversations] tableData 内容:', this.tableData);
        console.log('[AdminConversations] pagination.total:', this.pagination.total);
        console.log('[AdminConversations] 表格是否应该渲染:', this.tableData.length > 0 ? '是' : '否（空数据）');
      } catch (error) {
        console.error('[AdminConversations] 加载对话列表失败:', error);
        console.error('[AdminConversations] 错误详情:', error.message, error.response);
        showError('加载对话列表失败');
      } finally {
        this.loading = false;
      }
    },

    handlePageChange(page) {
      this.pagination.page = page;
      this.loadConversations();
    },

    /**
     * 查看对话消息详情 - 排查点：
     * 1. 检查对话ID是否正确传递
     * 2. 检查接口调用是否成功
     * 3. 检查返回数据结构是否正确（messages 和 statistics）
     * 4. 检查每条消息的字段是否完整（user_question, ai_response等）
     */
    async viewMessages(row) {
      this.currentConversationId = row.id;
      this.dialogTitle = row.title || '对话详情';
      this.dialogVisible = true;
      this.loadingMessages = true;
      this.messages = [];
      this.conversationStats = null;
      
      try {
        console.log('[AdminConversations] 开始加载对话消息详情...');
        console.log('[AdminConversations] 对话ID:', row.id);
        
        const res = await admin.getConversationDetail(row.id);
        console.log('[AdminConversations] 对话详情接口返回:', res);
        
        // 排查：检查响应结构
        if (!res || !res.data) {
          console.error('[AdminConversations] 错误：对话详情接口返回为空或没有data字段');
          this.messages = [];
          return;
        }
        
        // 排查：检查消息列表
        const messages = res.data.messages || [];
        const stats = res.data.statistics || null;
        console.log('[AdminConversations] 消息列表长度:', messages.length);
        console.log('[AdminConversations] 对话统计:', stats);
        
        // 排查：检查第一条消息的字段
        if (messages.length > 0) {
          console.log('[AdminConversations] 第一条消息详情:', {
            user_question: messages[0].user_question,
            ai_response: messages[0].ai_response,
            thinking_content: messages[0].thinking_content,
            created_at: messages[0].created_at,
            responded_at: messages[0].responded_at,
            token_count: messages[0].token_count,
            model: messages[0].model
          });
        }
        
        this.messages = messages;
        this.conversationStats = stats;
      } catch (error) {
        console.error('[AdminConversations] 加载消息失败:', error);
        console.error('[AdminConversations] 错误详情:', error.message, error.response);
        showError('加载消息失败');
        this.messages = [];
      } finally {
        this.loadingMessages = false;
      }
    },

    async handleDelete(row) {
      try {
        await ElMessageBox.confirm(`确定要删除对话 "${row.title}" 吗？此操作不可恢复。`, '警告', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        });
        await admin.deleteConversation(row.id);
        row.is_deleted = true;
        showSuccess('删除成功');
      } catch (error) {
        if (error !== 'cancel') {
          showError(error.message || '删除失败');
        }
      }
    },

    async handleRestore(row) {
      try {
        await ElMessageBox.confirm(`确定要恢复对话 "${row.title}" 吗？`, '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'info'
        });
        await admin.restoreConversation(row.id);
        row.is_deleted = false;
        showSuccess('恢复成功');
      } catch (error) {
        if (error !== 'cancel') {
          showError(error.message || '恢复失败');
        }
      }
    },

    formatTime(time) {
      if (!time) return '-';
      const date = new Date(time);
      return date.toLocaleString('zh-CN');
    }
  }
};
</script>

<style scoped>
.admin-conversations { padding: 0; }

.filter-card {
  margin-bottom: 16px;
  border-radius: 8px;
}
.light .filter-card { background: #fff; }

.filter-bar {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.table-card {
  border-radius: 8px;
}
.light .table-card { background: #fff; }

.pagination-wrap {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.dialog-stats {
  display: flex;
  gap: 20px;
  padding: 12px 16px;
  background: #f5f5f5;
  border-radius: 8px;
  margin-bottom: 16px;
  font-size: 13px;
  color: #666;
}
.dialog-stats span { display: flex; align-items: center; gap: 4px; }

.messages-container {
  max-height: 60vh;
  overflow-y: auto;
  padding: 10px;
  background: #f5f5f5;
  border-radius: 8px;
}

.message-item {
  margin-bottom: 16px;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0,0,0,0.1);
}
.message-item:last-child { margin-bottom: 0; }

.message-qa { display: flex; flex-direction: column; }

.qa-item {
  padding: 16px;
}
.qa-item.user {
  background: #e8f4ff;
  border-bottom: 1px solid #d0e8ff;
}
.qa-item.assistant {
  background: #fff;
}
.qa-item.thinking {
  background: #fffbf0;
  border-top: 1px dashed #ffe8b0;
}

.qa-label {
  font-weight: 600;
  font-size: 12px;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 4px;
}
.qa-item.user .qa-label { color: #409eff; }
.qa-item.assistant .qa-label { color: #67c23a; }
.qa-item.thinking .qa-label { color: #e6a23c; }

.qa-content {
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}
.qa-item.user .qa-content { color: #333; }
.qa-item.assistant .qa-content { color: #333; }
.thinking-content {
  font-size: 13px;
  color: #666;
  background: #fffbf0;
}

.qa-time, .qa-meta {
  font-size: 11px;
  color: #999;
  margin-top: 8px;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
.qa-meta span { display: flex; align-items: center; gap: 2px; }
.thinking-indicator { color: #e6a23c; }

.empty-tip {
  text-align: center;
  padding: 40px 0;
  color: #999;
  font-size: 14px;
}

.light :deep(.el-table) {
  background: #fff;
}
.light :deep(.el-table th) {
  background: #f5f7fa;
}
.light :deep(.el-table tr:hover > td) {
  background: #f0f0f0 !important;
}
.light :deep(.el-table--striped .el-table__body tr.el-table__row--striped td) {
  background: #fafafa;
}
</style>
