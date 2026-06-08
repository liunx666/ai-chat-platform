<template>
  <!-- 聊天页面主容器 -->
  <div class="chat-page" :class="{ light: !isDark }">
    <!-- 左侧对话列表侧边栏 -->
    <div class="chat-sidebar" :class="{ show: sidebarVisible }">
      <div class="sidebar-header">
        <span>AI 对话</span>
        <!-- 深色/浅色模式切换 -->
        <el-switch v-model="isDark" active-text="" inactive-text="" @change="toggleTheme"></el-switch>
      </div>
      
      <!-- 新建对话按钮 -->
      <div class="sidebar-btn" @click="createConversation">
        <span>+</span> 新建对话
      </div>
      
      <!-- 对话列表 -->
      <div class="conversation-list" v-loading="loadingList">
        <div
          v-for="item in conversationList"
          :key="item.id"
          :class="['conversation-item', { active: item.id === currentConversationId }]"
          @click="selectConversation(item)"
        >
          <span class="conversation-title">{{ item.title }}</span>
          <!-- 对话操作菜单 -->
          <el-dropdown trigger="click" @command="(cmd) => handleConversationCommand(cmd, item)">
            <span class="conversation-actions" @click.stop>
              <i class="el-icon-more"></i>
            </span>
            <el-dropdown-menu slot="dropdown">
              <el-dropdown-item command="rename">重命名</el-dropdown-item>
              <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
            </el-dropdown-menu>
          </el-dropdown>
        </div>
        <!-- 空状态提示 -->
        <div v-if="conversationList.length === 0 && !loadingList" class="empty-list">
          暂无对话记录
        </div>
      </div>
      
      <!-- 侧边栏底部操作 -->
      <div class="sidebar-actions">
        <el-button size="small" @click="$router.push('/password')">修改密码</el-button>
      </div>
    </div>

    <!-- 主聊天区域 -->
    <div class="chat-main">
      <!-- 聊天头部 -->
      <div class="chat-header">
        <div class="header-left">
          <!-- 移动端菜单按钮 -->
          <div class="mobile-menu" @click="sidebarVisible = !sidebarVisible">
            <i class="el-icon-s-fold"></i>
          </div>
          <span class="current-title" v-if="currentConversationId">{{ currentTitle }}</span>
        </div>
        <div class="header-right">
          <!-- 用户信息下拉菜单 -->
          <el-dropdown trigger="click" @command="handleCommand">
            <div class="user-info">
              <div class="user-avatar">{{ userInitial }}</div>
              <span class="user-name">{{ username }}</span>
              <i class="el-icon-arrow-down"></i>
            </div>
            <el-dropdown-menu slot="dropdown">
              <el-dropdown-item command="password">修改密码</el-dropdown-item>
              <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </el-dropdown>
        </div>
      </div>

      <!-- 消息列表区域 -->
      <div class="chat-messages" ref="list" @click="sidebarVisible = false">
        <!-- 消息项 -->
        <div v-for="(msg, i) in messages" :key="i" :class="['message', msg.role]">
          <div class="message-avatar">{{ msg.role === 'user' ? 'U' : 'G' }}</div>
          <div class="message-bubble">
            <!-- 深度思考内容 -->
            <div v-if="msg.thinking && isThinking" class="thinking-box">
              <div class="thinking-header" @click="msg.thinkingVisible = !msg.thinkingVisible">
                <span>深度思考</span>
                <i :class="msg.thinkingVisible ? 'el-icon-arrow-up' : 'el-icon-arrow-down'"></i>
              </div>
              <div v-show="msg.thinkingVisible" class="thinking-body markdown-body" v-html="renderMarkdown(msg.thinking)"></div>
            </div>
            <!-- 用户消息 -->
            <div class="markdown-body" v-if="msg.role === 'user'">{{ msg.content }}</div>
            <!-- AI消息（支持Markdown渲染） -->
            <div class="markdown-body" v-else v-html="renderMarkdown(msg.content)"></div>
          </div>
        </div>
        <!-- 加载状态 -->
        <div v-if="loading" class="message assistant">
          <div class="message-avatar">G</div>
          <div class="message-bubble loading-bubble">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
          </div>
        </div>
        <!-- 欢迎区域 -->
        <div v-if="messages.length === 0 && !loading" class="welcome-area">
          <div class="welcome-icon">G</div>
          <div class="welcome-text" v-html="welcomeMsg"></div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="chat-footer" @click="sidebarVisible = false">
        <div class="footer-options">
          <el-checkbox v-model="isThinking">深度思考</el-checkbox>
        </div>
        <div class="chat-input-area">
          <el-input
            v-model="input"
            placeholder="输入问题..."
            :disabled="loading"
            @keyup.enter.native="send"
            class="chat-input"
          ></el-input>
          <el-button type="primary" @click="send" :disabled="loading || !input.trim()">发送</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * @file 聊天页面组件
 * @description AI对话主页面，支持多对话管理、流式输出、Markdown渲染
 * @author aichat_upend
 */

import { marked } from 'marked';
import hljs from 'highlight.js';
import { chat, conversation, auth } from '@/api';
import { showSuccess, showError, showWarning } from '@/utils';

// 配置Markdown渲染
marked.setOptions({
  highlight: function(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value;
    }
    return hljs.highlightAuto(code).value;
  },
  breaks: true
});

export default {
  name: 'Chat',

  /**
   * 组件数据定义
   */
  data() {
    return {
      welcomeMsg: '&nbsp;&nbsp;你好！我是你的智能助手 GLM～<br/>&nbsp;&nbsp;点击左侧对话列表，可查看历史对话',
      input: '',                    // 用户输入内容
      sidebarVisible: false,        // 侧边栏显示状态
      loading: false,               // 发送消息加载状态
      loadingList: false,           // 对话列表加载状态
      messages: [],                 // 当前对话消息列表
      conversationList: [],         // 所有对话列表
      currentConversationId: null,  // 当前选中对话ID
      currentTitle: '新对话',       // 当前对话标题
      isThinking: false             // 是否开启深度思考模式
    };
  },

  /**
   * 计算属性
   */
  computed: {
    /**
     * 获取当前主题模式
     */
    isDark() {
      return this.$store.getters.isDark;
    },
    /**
     * 获取当前用户名
     */
    username() {
      const user = this.$store.getters.currentUser;
      return user.username || '用户';
    },
    /**
     * 获取用户名首字母（用于头像显示）
     */
    userInitial() {
      return this.username.charAt(0).toUpperCase();
    }
  },

  /**
   * 组件挂载时执行
   */
  mounted() {
    this.loadConversationList();
  },

  /**
   * 组件方法
   */
  methods: {
    /**
     * 切换主题模式（深色/浅色）
     */
    toggleTheme() {
      this.$store.dispatch('toggleTheme');
    },

    /**
     * 处理用户命令
     * @param {string} cmd - 命令类型（password/logout）
     */
    handleCommand(cmd) {
      if (cmd === 'password') {
        this.$router.push('/password');
      } else if (cmd === 'logout') {
        this.handleLogout();
      }
    },

    /**
     * 渲染Markdown内容
     * @param {string} content - Markdown内容
     * @returns {string} - HTML内容
     */
    renderMarkdown(content) {
      if (!content) return '';
      let html = marked(content);
      const tempDiv = document.createElement('div');
      tempDiv.innerHTML = html;
      // 为代码块添加复制按钮
      tempDiv.querySelectorAll('pre').forEach(pre => {
        const code = pre.querySelector('code');
        const copyBtn = document.createElement('button');
        copyBtn.className = 'copy-btn';
        copyBtn.textContent = '复制';
        copyBtn.onclick = (e) => {
          e.stopPropagation();
          navigator.clipboard.writeText(code.textContent);
          copyBtn.textContent = '已复制';
          setTimeout(() => copyBtn.textContent = '复制', 2000);
        };
        pre.style.position = 'relative';
        pre.appendChild(copyBtn);
      });
      return tempDiv.innerHTML;
    },

    /**
     * 加载对话列表
     */
    async loadConversationList() {
      this.loadingList = true;
      try {
        const res = await conversation.getList({ page: 1, page_size: 100 });
        this.conversationList = res.data.items || [];
        console.log('[Loaded Conversations]:', this.conversationList);
      } catch (error) {
        console.error('[Load Conversation List Error]:', error);
      } finally {
        this.loadingList = false;
      }
    },

    /**
     * 创建新对话
     */
    async createConversation() {
      try {
        const res = await conversation.create({ title: '新对话' });
        const newConv = res.data;
        this.conversationList.unshift(newConv);
        this.selectConversation(newConv);
        this.sidebarVisible = false;
      } catch (error) {
        showError('创建对话失败');
      }
    },

    /**
     * 选择对话
     * @param {Object} item - 对话项
     */
    async selectConversation(item) {
      // 如果已选中当前对话，仅关闭侧边栏
      if (this.currentConversationId === item.id) {
        this.sidebarVisible = false;
        return;
      }
      this.loading = true;
      this.currentConversationId = item.id;
      this.currentTitle = item.title;
      this.sidebarVisible = false;

      try {
        const res = await conversation.getDetail(item.id);
        console.log(res);
        
        // 转换消息格式 - 将每条问答对拆分成两条消息
        const messageList = [];
        (res.data.messages || []).forEach(msg => {
          // 添加用户消息
          if (msg.user_question) {
            messageList.push({
              role: 'user',
              content: msg.user_question,
              thinking: '',
              thinkingVisible: false
            });
          } else if (msg.content && msg.role === 'user') {
            messageList.push({
              role: 'user',
              content: msg.content,
              thinking: '',
              thinkingVisible: false
            });
          }
          
          // 添加AI消息
          if (msg.ai_response) {
            messageList.push({
              role: 'assistant',
              content: msg.ai_response,
              thinking: msg.thinking_content || '',
              thinkingVisible: false
            });
          } else if (msg.content && msg.role === 'assistant') {
            messageList.push({
              role: 'assistant',
              content: msg.content,
              thinking: msg.thinking_content || '',
              thinkingVisible: false
            });
          }
        });
        this.messages = messageList;
      } catch (error) {
        showError('加载对话失败');
        this.messages = [];
      } finally {
        this.loading = false;
      }
    },

    /**
     * 处理对话操作命令
     * @param {string} cmd - 命令类型（rename/delete）
     * @param {Object} item - 对话项
     */
    handleConversationCommand(cmd, item) {
      if (cmd === 'rename') {
        this.renameConversation(item);
      } else if (cmd === 'delete') {
        this.deleteConversation(item);
      }
    },

    /**
     * 重命名对话
     * @param {Object} item - 对话项
     */
    async renameConversation(item) {
      this.$prompt('请输入新标题', '重命名对话', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputValue: item.title
      }).then(async ({ value }) => {
        try {
          await conversation.update(item.id, { title: value });
          item.title = value;
          if (this.currentConversationId === item.id) {
            this.currentTitle = value;
          }
          showSuccess('修改成功');
        } catch (error) {
          showError('修改失败');
        }
      }).catch(() => {});
    },

    /**
     * 删除对话
     * @param {Object} item - 对话项
     */
    async deleteConversation(item) {
      try {
        await this.$confirm('确定要删除这个对话吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        });
        await conversation.remove(item.id);
        // 从列表中移除
        this.conversationList = this.conversationList.filter(c => c.id !== item.id);
        // 如果删除的是当前对话，重置状态
        if (this.currentConversationId === item.id) {
          this.currentConversationId = null;
          this.currentTitle = '新对话';
          this.messages = [];
        }
        showSuccess('删除成功');
      } catch (error) {
        if (error !== 'cancel') {
          showError('删除失败');
        }
      }
    },

    /**
     * 发送消息
     */
    async send() {
      // 验证输入
      if (!this.input.trim() || this.loading) return;

      const question = this.input;
      // 添加用户消息到列表
      this.messages.push({ role: 'user', content: question, thinking: '', thinkingVisible: false });
      this.input = '';
      this.loading = true;

      let fullContent = '';
      let fullThinking = '';

      try {
        // 调用流式聊天接口
        chat({
          question,
          conversation_id: this.currentConversationId || '',
          isThinking: this.isThinking
        }, (chunk) => {
          try {
            if (!chunk) return;
            // 按行解析SSE响应
            const lines = chunk.split('\n').filter(line => line.trim());
            for (const line of lines) {
              if (line === '[DONE]') continue;
              if (line.startsWith('data:')) {
                const jsonStr = line.slice(5).trim();
                if (!jsonStr || jsonStr === '[DONE]') continue;
                const data = JSON.parse(jsonStr);
                // 累积内容
                if (data.content) {
                  fullContent += data.content;
                }
                if (data.thinking) {
                  fullThinking += data.thinking;
                  // 更新或创建AI消息
                  const lastMsg = this.messages[this.messages.length - 1];
                  if (lastMsg.role === 'user') {
                    this.messages.push({ role: 'assistant', content: fullContent, thinking: fullThinking, thinkingVisible: true });
                  } else {
                    lastMsg.content = fullContent;
                    lastMsg.thinking = fullThinking;
                  }
                } else if (data.content) {
                  const lastMsg = this.messages[this.messages.length - 1];
                  if (lastMsg.role === 'user') {
                    this.messages.push({ role: 'assistant', content: fullContent, thinking: '', thinkingVisible: false });
                  } else {
                    lastMsg.content = fullContent;
                  }
                }
                // 处理流式结束
                if (data.end && data.conversation_id) {
                  this.handleStreamEnd(data, fullContent, fullThinking);
                }
              }
            }
          } catch (e) {
            console.error('[Parse Error]:', e);
          }
        });
      } catch (error) {
        showError(error.message || '发送消息失败');
        this.messages.push({ role: 'assistant', content: '抱歉，出错了', thinking: '', thinkingVisible: false });
      } finally {
        this.loading = false;
      }
    },

    /**
     * 处理流式响应结束
     * @param {Object} data - 响应数据
     * @param {string} fullContent - 完整内容
     * @param {string} fullThinking - 完整思考内容
     */
    async handleStreamEnd(data, fullContent, fullThinking) {
      // 如果是新对话，添加到对话列表
      if (data.conversation_id && !this.currentConversationId) {
        this.currentConversationId = data.conversation_id;
        this.currentTitle = '新对话';
        this.conversationList.unshift({
          id: data.conversation_id,
          title: '新对话',
          created_at: new Date().toISOString()
        });
      }
    },

    /**
     * 处理退出登录
     */
    async handleLogout() {
      try { await auth.logout(); } catch {}
      this.$store.dispatch('logout');
      this.$router.push('/login');
    }
  }
};
</script>

<style scoped>
/* 主页面样式 */
.chat-page { display: flex; height: 100vh; background: #ffffff; color: #333; }

/* 侧边栏样式 */
.chat-sidebar { width: 260px; background: #f7f7f7; border-right: 1px solid #e5e5e5; display: flex; flex-direction: column; flex-shrink: 0; }
.sidebar-header { padding: 16px; font-size: 16px; font-weight: 600; border-bottom: 1px solid #e5e5e5; display: flex; justify-content: space-between; align-items: center; }
.sidebar-btn { margin: 12px; padding: 10px 14px; border: 1px solid #e5e5e5; border-radius: 8px; cursor: pointer; display: flex; align-items: center; gap: 8px; font-size: 14px; transition: all 0.2s; background: #fff; color: #333; }
.sidebar-btn:hover { background: #f0f0f0; border-color: #d0d0d0; }
.conversation-list { flex: 1; overflow-y: auto; padding: 8px; }

/* 对话项样式 */
.conversation-item { padding: 10px 12px; margin-bottom: 4px; border-radius: 6px; cursor: pointer; transition: background 0.2s; display: flex; justify-content: space-between; align-items: center; }
.conversation-item:hover { background: #e8e8e8; }
.conversation-item.active { background: #e8f4ff; }
.conversation-title { font-size: 14px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex: 1; margin-right: 8px; }
.conversation-actions { opacity: 0; transition: opacity 0.2s; color: #999; padding: 4px; }
.conversation-item:hover .conversation-actions { opacity: 1; }
.conversation-actions:hover { color: #666; }

/* 空状态 */
.empty-list { text-align: center; padding: 40px 20px; color: #999; font-size: 14px; }

/* 侧边栏底部操作 */
.sidebar-actions { padding: 12px; border-top: 1px solid #e5e5e5; display: flex; flex-direction: column; gap: 8px; }

/* 主聊天区域 */
.chat-main { flex: 1; display: flex; flex-direction: column; min-width: 0; }
.chat-header { display: flex; justify-content: space-between; align-items: center; padding: 0 20px; height: 56px; border-bottom: 1px solid #e5e5e5; background: #fff; flex-shrink: 0; }
.header-left { display: flex; align-items: center; gap: 12px; }
.header-right { display: flex; align-items: center; }

/* 移动端菜单按钮 */
.mobile-menu { font-size: 22px; cursor: pointer; display: none; }

/* 当前标题 */
.current-title { font-size: 16px; font-weight: 500; }

/* 用户信息 */
.user-info { display: flex; align-items: center; gap: 8px; cursor: pointer; padding: 6px 12px; border-radius: 24px; transition: background 0.2s; }
.user-info:hover { background: #f0f0f0; }
.user-avatar { width: 30px; height: 30px; border-radius: 50%; background: linear-gradient(135deg, #667eea, #764ba2); display: flex; align-items: center; justify-content: center; font-weight: 600; font-size: 13px; color: #fff; }
.user-name { font-size: 14px; }

/* 消息列表区域 */
.chat-messages { flex: 1; overflow-y: auto; padding: 20px; background: #fff; }

/* 消息样式 */
.message { display: flex; gap: 12px; margin-bottom: 16px; }
.message.user { flex-direction: row-reverse; }
.message.assistant .message-bubble { background: #f0f0f0; color: #1f1f1f; }
.message.user .message-bubble { background: #5436da; color: #fff; }

/* 消息头像 */
.message-avatar { width: 36px; height: 36px; border-radius: 50%; background: #e0e0e0; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 600; flex-shrink: 0; }
.message.user .message-avatar { background: linear-gradient(135deg, #667eea, #764ba2); color: #fff; }
.message.assistant .message-avatar { background: #4caf50; color: #fff; }

/* 消息气泡 */
.message-bubble { max-width: 70%; padding: 10px 14px; border-radius: 14px; line-height: 1.5; word-break: break-word; font-size: 14px; }
.message.user .message-bubble { border-bottom-right-radius: 4px; }
.message.assistant .message-bubble { border-bottom-left-radius: 4px; }

/* 深度思考区域 */
.thinking-box { margin-bottom: 8px; padding: 8px; background: #fffbe6; border-radius: 8px; border: 1px solid #ffe082; }
.thinking-header { display: flex; justify-content: space-between; align-items: center; font-size: 12px; font-weight: 500; color: #f57c00; cursor: pointer; }
.thinking-body { margin-top: 8px; font-size: 13px; color: #5d4037; }

/* 加载状态 */
.loading-bubble { display: flex; gap: 6px; padding: 12px 16px; }
.typing-dot { width: 8px; height: 8px; border-radius: 50%; background: #999; animation: typing 1.4s infinite ease-in-out; }
.typing-dot:nth-child(1) { animation-delay: 0s; }
.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.5; }
  40% { transform: scale(1); opacity: 1; }
}

/* 欢迎区域 */
.welcome-area { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 60px 20px; }
.welcome-icon { width: 80px; height: 80px; border-radius: 50%; background: linear-gradient(135deg, #667eea, #764ba2); display: flex; align-items: center; justify-content: center; font-size: 36px; font-weight: 600; color: #fff; margin-bottom: 16px; }
.welcome-text { font-size: 18px; color: #666; }

/* 输入区域 */
.chat-footer { padding: 16px 20px; border-top: 1px solid #e5e5e5; background: #fff; flex-shrink: 0; }
.footer-options { margin-bottom: 12px; }
.chat-input-area { display: flex; gap: 12px; }
.chat-input { flex: 1; }

/* Markdown样式 */
.markdown-body { font-size: 14px; line-height: 1.6; }
.markdown-body code { padding: 2px 4px; background: #f0f0f0; border-radius: 4px; font-size: 13px; }
.markdown-body pre { padding: 12px; background: #1f1f1f; border-radius: 8px; overflow-x: auto; margin: 8px 0; }
.markdown-body pre code { background: transparent; color: #e0e0e0; padding: 0; font-size: 13px; }
.markdown-body blockquote { border-left: 4px solid #409eff; padding-left: 12px; margin: 8px 0; color: #666; background: #f5f7fa; padding: 8px 12px; border-radius: 0 4px 4px 0; }
.markdown-body table { width: 100%; border-collapse: collapse; margin: 8px 0; }
.markdown-body th, .markdown-body td { border: 1px solid #e5e5e5; padding: 8px; text-align: left; }
.markdown-body th { background: #f5f7fa; }
.markdown-body img { max-width: 100%; border-radius: 4px; }
.markdown-body ul, .markdown-body ol { padding-left: 24px; margin: 8px 0; }
.markdown-body li { margin: 4px 0; }
.markdown-body h1 { font-size: 24px; margin: 16px 0; padding-bottom: 8px; border-bottom: 1px solid #e5e5e5; }
.markdown-body h2 { font-size: 20px; margin: 14px 0; }
.markdown-body h3 { font-size: 18px; margin: 12px 0; }
.markdown-body h4, .markdown-body h5, .markdown-body h6 { font-size: 16px; margin: 10px 0; }
.markdown-body hr { border: none; border-top: 1px solid #e5e5e5; margin: 16px 0; }

/* 代码复制按钮 */
.copy-btn { position: absolute; top: 8px; right: 8px; padding: 4px 10px; font-size: 12px; background: #333; color: #fff; border: none; border-radius: 4px; cursor: pointer; transition: background 0.2s; }
.copy-btn:hover { background: #444; }

/* 响应式布局 */
@media (max-width: 768px) {
  .chat-sidebar { position: fixed; top: 0; left: -280px; z-index: 1000; height: 100vh; transition: left 0.3s; width: 80%; max-width: 300px; }
  .chat-sidebar.show { left: 0; box-shadow: 4px 0 20px rgba(0,0,0,0.3); }
  .mobile-menu { display: block; }
  .chat-header { padding: 0 16px; }
  .chat-messages { padding: 16px; }
  .message-bubble { max-width: 85%; }
  .chat-footer { padding: 12px 16px; }
}
</style>