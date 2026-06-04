import { createRouter, createWebHistory } from 'vue-router'
import StoreHomeView from '../views/StoreHomeView.vue'
import AdminDashboardView from '../views/AdminDashboardView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'store-home',
      component: StoreHomeView
    },
    {
      path: '/admin',
      name: 'admin-dashboard',
      component: AdminDashboardView
    }
  ]
})

export default router

