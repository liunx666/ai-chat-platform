import { createStore } from 'vuex'

const STORAGE_KEYS = {
  TOKEN: 'token',
  USER: 'user',
  THEME: 'theme'
}

export default createStore({
  state: {
    token: localStorage.getItem(STORAGE_KEYS.TOKEN) || '',
    user: JSON.parse(localStorage.getItem(STORAGE_KEYS.USER) || '{}'),
    isDark: localStorage.getItem(STORAGE_KEYS.THEME) !== 'light'
  },

  mutations: {
    SET_TOKEN(state, token) {
      state.token = token
      localStorage.setItem(STORAGE_KEYS.TOKEN, token)
    },

    SET_USER(state, user) {
      state.user = user
      localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(user))
    },

    CLEAR_AUTH(state) {
      state.token = ''
      state.user = {}
      localStorage.removeItem(STORAGE_KEYS.TOKEN)
      localStorage.removeItem(STORAGE_KEYS.USER)
    },

    SET_THEME(state, isDark) {
      state.isDark = isDark
      localStorage.setItem(STORAGE_KEYS.THEME, isDark ? 'dark' : 'light')
    }
  },

  actions: {
    login({ commit }, { token, user }) {
      commit('SET_TOKEN', token)
      commit('SET_USER', user)
    },

    logout({ commit }) {
      commit('CLEAR_AUTH')
    },

    toggleTheme({ commit, state }) {
      commit('SET_THEME', !state.isDark)
    }
  },

  getters: {
    isLoggedIn: state => !!state.token,
    currentUser: state => state.user,
    isDark: state => state.isDark,
    isAdmin: state => state.user.role === 'admin',
    tenantId: state => state.user.tenant_id || 'default'
  }
})
