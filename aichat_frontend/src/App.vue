<template>
  <div id="app" :class="{ 'mobile': isMobile }">
    <router-view></router-view>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const isMobile = ref(false)

const checkDevice = () => {
  isMobile.value = window.innerWidth <= 768
}

onMounted(() => {
  checkDevice()
  window.addEventListener('resize', checkDevice)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', checkDevice)
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html,
body,
#app {
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC',
    'Hiragino Sans GB', 'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial,
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.chat-page:not(.light) .markdown-body {
  color: #e5e5e5;
}

.chat-page:not(.light) .markdown-body pre {
  background: rgba(0, 0, 0, 0.3);
}

.chat-page:not(.light) .markdown-body code {
  background: rgba(0, 0, 0, 0.2);
}

.chat-page.light .markdown-body {
  color: #1f1f1f;
}

.chat-page.light .markdown-body pre {
  background: rgba(0, 0, 0, 0.05);
}

.chat-page.light .markdown-body code {
  background: rgba(0, 0, 0, 0.08);
}
</style>
