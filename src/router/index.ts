import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/pages/Home.vue'
import Settings from '@/pages/Settings.vue'
import Editor from '@/pages/Editor.vue'
// 定义路由组件

const routes = [
  {
    path: '/',
    component: Home
  },
  {
    path: '/settings',
    component: Settings
  },
  {
    path: '/editor',
    component: Editor
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router