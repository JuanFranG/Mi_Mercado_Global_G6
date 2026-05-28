<script setup lang="ts">
import { ref } from 'vue'
import { useAppStore } from '../stores/app'
import UserProfile from '../components/UserProfile.vue'
import RecentOrders from '../components/RecentOrders.vue'
import OrderDetail from '../components/OrderDetail.vue'

const app = useAppStore()
const pedidoSeleccionado = ref('555')
</script>

<template>
  <div class="pedidos-layout">
    <div class="sidebar">
      <UserProfile :usuarioId="app.usuarioId" />
      <RecentOrders
        :usuarioId="app.usuarioId"
        :seleccionado="pedidoSeleccionado"
        @seleccionar="(id: string) => pedidoSeleccionado = id"
      />
    </div>
    <OrderDetail :idPedido="pedidoSeleccionado" />
  </div>
</template>

<style scoped>
.pedidos-layout {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 2rem;
  max-width: 1280px;
  margin: 2rem auto;
  padding: 0 2rem;
  align-items: start;
}

@media (max-width: 992px) {
  .pedidos-layout { grid-template-columns: 1fr; }
}

.sidebar {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}
</style>
