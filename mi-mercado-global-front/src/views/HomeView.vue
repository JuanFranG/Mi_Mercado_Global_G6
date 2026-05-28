<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { RouterLink } from 'vue-router'
import ProductCard from '../components/ProductCard.vue'
import { useAppStore } from '../stores/app'

const app = useAppStore()

const CATEGORIAS = ['Todos', 'Electronica', 'Ropa', 'Hogar', 'Deportes']
const LABELS: Record<string, string> = {
  Todos: 'Todos', Electronica: 'Electrónica', Ropa: 'Ropa',
  Hogar: 'Hogar', Deportes: 'Deportes',
}

const categoriaActual = ref('Todos')
const productos       = ref<any[]>([])
const cargando        = ref(false)
const fuente          = ref('')

const cargar = async (cat: string) => {
  cargando.value = true
  try {
    const url  = cat === 'Todos' ? '/api/productos' : `/api/productos?categoria=${cat}`
    const res  = await fetch(url)
    const data = await res.json()
    productos.value = data.productos ?? []
    fuente.value    = data.fuente ?? ''
  } catch {
    productos.value = []
  } finally {
    cargando.value = false
  }
}

const productosFiltrados = computed(() => {
  const q = app.searchQuery.trim().toLowerCase()
  if (!q) return productos.value
  return productos.value.filter(p =>
    p.Nombre.toLowerCase().includes(q) ||
    (p.Descripcion ?? '').toLowerCase().includes(q)
  )
})

onMounted(() => cargar('Todos'))
watch(categoriaActual, cargar)
</script>

<template>
  <div class="catalog-layout">
    <!-- Sidebar de categorías -->
    <aside class="category-sidebar">
      <h3 class="sidebar-title">Categorías</h3>
      <ul class="category-list">
        <li
          v-for="cat in CATEGORIAS"
          :key="cat"
          class="category-item"
          :class="{ active: categoriaActual === cat }"
          @click="categoriaActual = cat"
        >
          {{ LABELS[cat] }}
        </li>
      </ul>

      <div v-if="fuente" class="cache-badge" :class="fuente">
        {{ fuente === 'cache' ? 'Redis cache' : 'DynamoDB' }}
      </div>

    </aside>

    <!-- Grid de productos -->
    <main class="product-main">
      <div class="product-main-header">
        <h2>{{ LABELS[categoriaActual] }}</h2>
        <span class="product-count">{{ productosFiltrados.length }} productos</span>
      </div>

      <div v-if="cargando" class="loading">Cargando productos…</div>

      <div v-else-if="productos.length === 0" class="empty">
        No hay productos en esta categoría.
      </div>

      <div v-else class="product-grid">
        <ProductCard
          v-for="p in productosFiltrados"
          :key="p.PK"
          :producto="p"
        />
      </div>
    </main>
  </div>
</template>

<style scoped>
.catalog-layout {
  display: grid;
  grid-template-columns: 220px 1fr;
  gap: 2rem;
  max-width: 1280px;
  margin: 2rem auto;
  padding: 0 2rem;
  align-items: start;
}

/* ── Sidebar ── */
.category-sidebar {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 12px;
  padding: 1.25rem;
  position: sticky;
  top: 76px;
}

.sidebar-title {
  font-size: .8125rem;
  text-transform: uppercase;
  letter-spacing: .05em;
  color: #6e6e73;
  margin-bottom: 1rem;
}

.category-list { list-style: none; }

.category-item {
  padding: .625rem .75rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: .9375rem;
  color: #1d1d1f;
  transition: background .1s;
}
.category-item:hover  { background: #f5f5f7; }
.category-item.active {
  background: #e8f0fe;
  color: #1a73e8;
  font-weight: 600;
}

.cache-badge {
  margin-top: 1.5rem;
  font-size: .75rem;
  padding: .35rem .6rem;
  border-radius: 20px;
  text-align: center;
}
.cache-badge.cache    { background: #fef9c3; color: #854d0e; }
.cache-badge.dynamodb { background: #dcfce7; color: #166534; }


/* ── Main ── */
.product-main-header {
  display: flex;
  align-items: baseline;
  gap: 1rem;
  margin-bottom: 1.5rem;
}
.product-main-header h2 { font-size: 1.25rem; }
.product-count {
  font-size: .875rem;
  color: #6e6e73;
}

.loading, .empty {
  color: #6e6e73;
  text-align: center;
  padding: 3rem;
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
  gap: 1.25rem;
}

@media (max-width: 768px) {
  .catalog-layout { grid-template-columns: 1fr; }
  .category-sidebar { position: static; }
}
</style>
