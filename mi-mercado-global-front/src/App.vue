<script setup>
import { ref } from 'vue';
import TheHeader from './components/TheHeader.vue';
import UserProfile from './components/UserProfile.vue';
import RecentOrders from './components/RecentOrders.vue';
import OrderDetail from './components/OrderDetail.vue';

const pedidoSeleccionado = ref('555');

const cambiarPedido = (id) => {
  pedidoSeleccionado.value = id;
};
</script>

<template>
  <TheHeader />
  <main class="layout-container">
    <div class="sidebar">
    <UserProfile usuarioId="550e8400-e29b-41d4-a716-446655440000" />
    <RecentOrders usuarioId="550e8400-e29b-41d4-a716-446655440000" :seleccionado="pedidoSeleccionado" @seleccionar="cambiarPedido" />
    </div>
    <OrderDetail :idPedido="pedidoSeleccionado" />
  </main>
</template>

<style>

.layout-container {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 2rem;
  max-width: 1280px;
  margin: 2rem auto;
  padding: 0 2rem;
  align-items: start;
}
.sidebar {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}
@media (max-width: 992px) {
  .layout-container {
    grid-template-columns: 1fr;
  }
}
</style>