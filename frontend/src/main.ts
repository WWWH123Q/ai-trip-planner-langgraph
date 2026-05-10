import { createApp } from 'vue' //创建vue应用
import { createRouter, createWebHistory } from 'vue-router' //创建前端路由系统
import Antd from 'ant-design-vue' //引入 Ant Design Vue 组件库
import 'ant-design-vue/dist/reset.css'
import App from './App.vue'//整个前端应用的根组件
import Home from './views/Home.vue' //首页表单页
import Result from './views/Result.vue' //结果展示页

// 创建路由 router：这段是前端页面跳转规则：
// 规定：
// 访问 /  --> 显示 Home.vue
// 访问 /result  -->显示 Result.vue
const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: Home
    },
    {
      path: '/result',
      name: 'Result',
      component: Result
    }
  ]
})
//创建Vue应用，以 App.vue 作为根组件，创建整个 Vue 前端应用
// 你可以类比后端：
// 后端：
// FastAPI(...) 创建 app
// 前端：
// createApp(App) 创建 app
const app = createApp(App)

//注册插件
app.use(router) //让整个前端应用支持路由跳转
app.use(Antd) //让整个前端应用可以使用 Ant Design Vue 组件

//挂载到页面：把 Vue 应用挂载到 HTML 页面中 id="app" 的节点上
app.mount('#app')


//流程
// main.ts
//   ↓
// App.vue
//   ↓
// router-view
//   ↓
// Home.vue 或 Result.vue