<script setup lang="ts">
import { ref } from 'vue'
import { useAppStore } from '../stores/app'

const props = defineProps<{
  producto: {
    PK: string; Nombre: string; Precio: number
    Stock: number; Categoria: string; Descripcion?: string
  }
}>()

const app = useAppStore()

const IMAGENES: Record<string, string> = {
  'Auriculares Bluetooth Z5':  '/productos/auriculares.jpg',
  'Portátil WorkPro 15':       '/productos/portatil.jpg',
  'Teléfono Inteligente X100': '/productos/celular.jpg',
  'Reloj Inteligente FitTrack':'/productos/reloj.jpg',
  'Balón de Fútbol Pro':       '/productos/balon.jpg',
  'Pesas Hexagonales 5 kg':    '/productos/pesas.jpg',
  'Mochila de Viaje 40L':      '/productos/mochila.jpg',
  'Licuadora MultiPro':        '/productos/licuadora.jpg',
  'Juego de Sábanas Queen':    '/productos/sabanas.jpg',
  'Camiseta Algodón Hombre':   '/productos/camiseta.jpg',
  'Jeans Slim Fit':            '/productos/jeans.png',
  'Chaqueta Deportiva':        '/productos/chaqueta.png',
  'Vestido Floral Verano':     '/productos/vestido.png',
}

const COLORES: Record<string, [string, string]> = {
  Electronica: ['#1a73e8', '#1557b0'],
  Ropa:        ['#7c3aed', '#5b21b6'],
  Hogar:       ['#ea580c', '#c2410c'],
  Deportes:    ['#16a34a', '#15803d'],
}
const [c1, c2] = COLORES[props.producto.Categoria] ?? ['#6e6e73', '#4b5563']
const imgSrc = IMAGENES[props.producto.Nombre] ?? null
const imgError = ref(false)

const formatPrecio = (p: number) =>
  new Intl.NumberFormat('es-CO', {
    style: 'currency', currency: 'COP', maximumFractionDigits: 0,
  }).format(p)

const agregar = () =>
  app.agregarAlCarrito({
    producto_id: props.producto.PK,
    nombre:      props.producto.Nombre,
    precio:      props.producto.Precio,
    cantidad:    1,
  })
</script>

<template>
  <div class="product-card">
    <div
      class="product-img"
      :style="(!imgSrc || imgError) ? { background: `linear-gradient(135deg, ${c1}, ${c2})` } : {}"
    >
      <img
        v-if="imgSrc && !imgError"
        :src="imgSrc"
        :alt="producto.Nombre"
        class="product-img-photo"
        @error="imgError = true"
      />
      <span class="product-cat-label">{{ producto.Categoria }}</span>
    </div>
    <div class="product-body">
      <p class="product-nombre">{{ producto.Nombre }}</p>
      <p class="product-precio">{{ formatPrecio(producto.Precio) }} COP</p>
      <p class="product-stock" :class="{ agotado: producto.Stock === 0 }">
        Stock: {{ producto.Stock }}
      </p>
      <button
        class="btn-carrito"
        :disabled="producto.Stock === 0"
        @click="agregar"
      >
        Añadir al Carrito
      </button>
    </div>
  </div>
</template>

<style scoped>
.product-card {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: box-shadow .2s, transform .2s;
}
.product-card:hover {
  box-shadow: 0 6px 20px rgba(0,0,0,.1);
  transform: translateY(-2px);
}

.product-img {
  height: 130px;
  position: relative;
  display: flex;
  align-items: flex-end;
  padding: .75rem;
  overflow: hidden;
}
.product-img-photo {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.product-cat-label {
  position: relative;
  background: rgba(0,0,0,.35);
  color: #fff;
  font-size: .75rem;
  font-weight: 600;
  padding: .2rem .55rem;
  border-radius: 20px;
  letter-spacing: .03em;
  backdrop-filter: blur(2px);
}

.product-body {
  padding: .875rem;
  display: flex;
  flex-direction: column;
  gap: .35rem;
  flex: 1;
}

.product-nombre {
  font-size: .9rem;
  font-weight: 600;
  color: #1d1d1f;
  line-height: 1.3;
}

.product-precio {
  font-size: 1rem;
  font-weight: 700;
  color: #1a73e8;
}

.product-stock {
  font-size: .8rem;
  color: #6e6e73;
}
.product-stock.agotado { color: #ea4335; }

.btn-carrito {
  margin-top: .5rem;
  background: #1a73e8;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: .55rem;
  font-size: .875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background .15s;
}
.btn-carrito:hover:not(:disabled) { background: #1557b0; }
.btn-carrito:disabled { background: #d1d5db; cursor: not-allowed; }
</style>
