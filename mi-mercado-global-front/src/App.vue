<script setup lang="ts">
import { onMounted } from 'vue'
import TheHeader from './components/TheHeader.vue'
import CartPanel from './components/CartPanel.vue'
import { useAppStore } from './stores/app'

const store = useAppStore()
onMounted(async () => {
  await Promise.all([store.cargarCarrito(), store.cargarPerfil()])
})
</script>

<template>
  <TheHeader />
  <RouterView />

  <footer class="site-footer">
    <RouterLink to="/mis-pedidos" class="footer-link">Mis Pedidos</RouterLink>
    <span class="footer-link muted">Soporte</span>
    <span class="footer-link muted">Política de Privacidad</span>
  </footer>

  <CartPanel />

  <!-- Toast de pedido creado -->
  <Transition name="toast">
    <div v-if="store.pedidoCreado" class="toast-success">
      Pedido #{{ store.pedidoCreado }} creado exitosamente
    </div>
  </Transition>
</template>

<style>
.site-footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
  border-top: 1px solid #e8e8e8;
  background: #f8f9fa;
  padding: .75rem 2rem;
  display: flex;
  gap: 2rem;
  font-size: .875rem;
}
.footer-link {
  color: #6e6e73;
  text-decoration: none;
  cursor: pointer;
}
.footer-link:not(.muted) {
  color: #1a73e8;
  font-weight: 500;
}
.footer-link:not(.muted):hover { text-decoration: underline; }

.toast-success {
  position: fixed;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);
  background: #166534;
  color: #fff;
  padding: .875rem 1.5rem;
  border-radius: 10px;
  font-size: .9375rem;
  font-weight: 500;
  box-shadow: 0 4px 16px rgba(0,0,0,.2);
  z-index: 999;
}
.toast-enter-active, .toast-leave-active { transition: all .3s; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateX(-50%) translateY(1rem); }
</style>
