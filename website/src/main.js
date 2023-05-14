import { createApp } from 'vue'
import App from './App.vue'

// import VueCookies from 'vue-cookies'

const app = createApp(App)

// default options config: { expires: '1d', path: '/', domain: '', secure: '', sameSite: 'Lax' }
// app.use(VueCookies, { expires: '7d'})
app.config.globalProperties.$api_v = 1
app.config.globalProperties.$host = `https://sky.jason.cash:8080/api/v${app.config.globalProperties.$api_v}`

app.mount('#app')
