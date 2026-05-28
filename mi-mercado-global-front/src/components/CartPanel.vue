<script setup lang="ts">
import { ref } from 'vue'
import { useAppStore } from '../stores/app'

const app      = useAppStore()
const enviando = ref(false)
const error    = ref('')

const formatPrecio = (p: number) =>
  new Intl.NumberFormat('es-CO', {
    style: 'currency', currency: 'COP', maximumFractionDigits: 0,
  }).format(p)

const pedir = async () => {
  if (!app.usuarioPerfil) {
    error.value = 'Cargando perfil de usuario, intenta de nuevo.'
    return
  }
  enviando.value = true
  error.value    = ''
  try {
    await app.realizarPedido()
  } catch (e) {
    error.value = 'Error al crear el pedido. Intenta de nuevo.'
  } finally {
    enviando.value = false
  }
}
</script>

<template>
  <Transition name="fade">
    <div v-if="app.cartAbierto" class="overlay" @click="app.cartAbierto = false" />
  </Transition>

  <Transition name="slide">
    <aside v-if="app.cartAbierto" class="cart-panel">
      <div class="cart-header">
        <h2>Carrito <span class="cart-count">({{ app.cantidadCarrito }})</span></h2>
        <button class="close-btn" @click="app.cartAbierto = false">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <path d="M18 6 6 18M6 6l12 12"/>
          </svg>
        </button>
      </div>

      <div v-if="app.carritoItems.length === 0" class="cart-empty">
        <p>Tu carrito está vacío</p>
      </div>

      <ul v-else class="cart-items">
        <li v-for="item in app.carritoItems" :key="item.producto_id" class="cart-item">
          <div class="item-info">
            <p class="item-nombre">{{ item.nombre }}</p>
            <p class="item-detalle">{{ formatPrecio(item.precio) }} × {{ item.cantidad }}</p>
          </div>
          <div class="item-right">
            <span class="item-subtotal">{{ formatPrecio(item.precio * item.cantidad) }}</span>
            <button class="remove-btn" @click="app.eliminarDelCarrito(item.producto_id)">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M18 6 6 18M6 6l12 12"/>
              </svg>
            </button>
          </div>
        </li>
      </ul>

      <div v-if="app.carritoItems.length > 0" class="cart-footer">
        <div class="total-row">
          <span>Total</span>
          <strong>{{ formatPrecio(app.totalCarrito) }}</strong>
        </div>

        <p v-if="error" class="error-msg">{{ error }}</p>

        <button class="btn-limpiar" @click="app.limpiarCarrito()">Limpiar carrito</button>
        <button class="btn-pedir" :disabled="enviando" @click="pedir">
          {{ enviando ? 'Procesando…' : 'Realizar Pedido' }}
        </button>
      </div>
    </aside>
  </Transition>
</template>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,.3);
  z-index: 300;
}

.cart-panel {
  position: fixed;
  top: 0; right: 0;
  width: 360px;
  height: 100vh;
  background: #fff;
  z-index: 400;
  display: flex;
  flex-direction: column;
  box-shadow: -4px 0 24px rgba(0,0,0,.12);
}

.cart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #e8e8e8;
}
.cart-header h2 { font-size: 1.0625rem; }
.cart-count { color: #6e6e73; font-weight: 400; }

.close-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #6e6e73;
  padding: .25rem;
}
.close-btn:hover { color: #1d1d1f; }

.cart-empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6e6e73;
  font-size: .9375rem;
}

.cart-items {
  list-style: none;
  flex: 1;
  overflow-y: auto;
}

.cart-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: .875rem 1.5rem;
  border-bottom: 1px solid #f0f0f0;
}

.item-nombre {
  font-size: .875rem;
  font-weight: 500;
  color: #1d1d1f;
  margin-bottom: .2rem;
}
.item-detalle { font-size: .8rem; color: #6e6e73; }

.item-right {
  display: flex;
  align-items: center;
  gap: .75rem;
  flex-shrink: 0;
  margin-left: 1rem;
}
.item-subtotal { font-size: .875rem; font-weight: 600; color: #1a73e8; }

.remove-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #9ca3af;
  padding: .15rem;
}
.remove-btn:hover { color: #ea4335; }

.cart-footer {
  padding: 1.25rem 1.5rem;
  border-top: 1px solid #e8e8e8;
  display: flex;
  flex-direction: column;
  gap: .75rem;
}

.total-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: .9375rem;
}
.total-row strong { font-size: 1.0625rem; }

.error-msg { font-size: .8125rem; color: #ea4335; }

.btn-limpiar {
  background: none;
  border: 1px solid #d1d1d1;
  border-radius: 8px;
  padding: .6rem;
  font-size: .875rem;
  color: #6e6e73;
  cursor: pointer;
}
.btn-limpiar:hover { border-color: #ea4335; color: #ea4335; }

.btn-pedir {
  background: #1a73e8;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: .75rem;
  font-size: .9375rem;
  font-weight: 600;
  cursor: pointer;
  transition: background .15s;
}
.btn-pedir:hover:not(:disabled) { background: #1557b0; }
.btn-pedir:disabled { background: #9ca3af; cursor: not-allowed; }

.fade-enter-active, .fade-leave-active { transition: opacity .25s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.slide-enter-active, .slide-leave-active { transition: transform .3s ease; }
.slide-enter-from, .slide-leave-to { transform: translateX(100%); }
</style>
