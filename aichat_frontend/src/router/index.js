import { createRouter, createWebHistory } from 'vue-router'
import store from '@/store'
import Login from '@/views/Login.vue'
import Register from '@/views/Register.vue'
import Chat from '@/views/Chat.vue'
import Password from '@/views/Password.vue'
import Admin from '@/views/admin/Admin.vue'
import AdminDashboard from '@/views/admin/AdminDashboard.vue'
import AdminUsers from '@/views/admin/AdminUsers.vue'
import AdminConversations from '@/views/admin/AdminConversations.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: Login,
      meta: { title: '登录 - AI对话' }
    },
    {
      path: '/register',
      name: 'Register',
      component: Register,
      meta: { title: '注册 - AI对话' }
    },
    {
      path: '/chat',
      name: 'Chat',
      component: Chat,
      meta: { requiresAuth: true, title: 'AI对话' }
    },
    {
      path: '/password',
      name: 'Password',
      component: Password,
      meta: { requiresAuth: true, title: '修改密码 - AI对话' }
    },
    {
      path: '/admin',
      component: Admin,
      meta: { requiresAuth: true, requiresAdmin: true, title: '管理后台' },
      children: [
        {
          path: '',
          name: 'AdminDashboard',
          component: AdminDashboard,
          meta: { title: '数据统计 - 管理后台' }
        },
        {
          path: 'users',
          name: 'AdminUsers',
          component: AdminUsers,
          meta: { title: '用户管理 - 管理后台' }
        },
        {
          path: 'conversations',
          name: 'AdminConversations',
          component: AdminConversations,
          meta: { title: '对话管理 - 管理后台' }
        }
      ]
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/login'
    }
  ]
})

router.beforeEach((to, from) => {
  const isLoggedIn = store.getters.isLoggedIn
  const isAdmin = store.getters.isAdmin

  if (to.meta.title) {
    document.title = to.meta.title
  }

  if (to.meta.requiresAuth) {
    if (!isLoggedIn) {
      return '/login'
    }
    if (to.meta.requiresAdmin && !isAdmin) {
      return '/chat'
    }
    return true
  } else {
    if (isLoggedIn && to.path === '/login') {
      const role = store.getters.currentUser.role
      if (role === 'admin') {
        return '/admin'
      } else {
        return '/chat'
      }
    }
    return true
  }
})

export default router
