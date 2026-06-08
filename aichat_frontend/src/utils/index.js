import { ElMessage } from 'element-plus'

export const showSuccess = (msg) => {
  ElMessage.success({
    message: msg,
    duration: 3000
  })
}

export const showError = (msg) => {
  ElMessage.error({
    message: msg,
    duration: 3000
  })
}

export const showWarning = (msg) => {
  ElMessage.warning({
    message: msg,
    duration: 3000
  })
}

export const showInfo = (msg) => {
  ElMessage.info({
    message: msg,
    duration: 3000
  })
}

export const debounce = (func, delay = 300) => {
  let timer = null
  return function(...args) {
    if (timer) {
      clearTimeout(timer)
    }
    timer = setTimeout(() => {
      func.apply(this, args)
    }, delay)
  }
}

export const throttle = (func, delay = 300) => {
  let lastTime = 0
  return function(...args) {
    const now = Date.now()
    if (now - lastTime >= delay) {
      func.apply(this, args)
      lastTime = now
    }
  }
}

export const formatDate = (date, format = 'YYYY-MM-DD HH:mm:ss') => {
  const d = new Date(date)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')

  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds)
}

export const copyToClipboard = async (text) => {
  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(text)
      return true
    }
    const textArea = document.createElement('textarea')
    textArea.value = text
    document.body.appendChild(textArea)
    textArea.select()
    document.execCommand('copy')
    document.body.removeChild(textArea)
    return true
  } catch (error) {
    console.error('[Copy Error]:', error)
    return false
  }
}

export const isMobile = () => {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
}

export const isSystemDark = () => {
  return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
}
