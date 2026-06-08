import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCNPlugin from './utils/zhCN'

const app = createApp(App)

app.config.productionTip = false

app.use(router)
app.use(store)
app.use(ElementPlus)
app.use(zhCNPlugin)

app.mount('#app')
