import { createRouter, createWebHistory } from 'vue-router'
import HomeView      from '../views/HomeView.vue'
import MisPedidosView from '../views/MisPedidosView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/',            name: 'home',       component: HomeView },
    { path: '/mis-pedidos', name: 'mis-pedidos', component: MisPedidosView },
  ],
})

export default router
