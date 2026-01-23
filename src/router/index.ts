import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/pages/Home.vue'
import Settings from '@/pages/Settings.vue'
// 定义路由组件

const routes = [
  {
    path: '/',
    component: Home
  },
  {
    path: '/settings',
    component: Settings
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router