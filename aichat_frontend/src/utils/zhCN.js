import { createI18n } from 'vue-i18n'
import zhCN from 'element-plus/es/locale/lang/zh-cn'

export default {
  install: (app) => {
    const i18n = createI18n({
      legacy: false,
      locale: 'zh-cn',
      messages: {
        'zh-cn': zhCN
      }
    })
    app.use(i18n)
  }
}
