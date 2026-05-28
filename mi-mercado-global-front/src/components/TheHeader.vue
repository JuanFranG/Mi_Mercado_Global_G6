<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../stores/app'

const router = useRouter()
const app    = useAppStore()

const mostrarPerfil = ref(false)
const usuarios      = ref<any[]>([])
const busqueda      = ref('')

onMounted(async () => {
  try {
    const res  = await fetch('/api/usuarios')
    const data = await res.json()
    usuarios.value = data.usuarios ?? []
  } catch {}
})

watch(busqueda, (val) => { app.searchQuery = val })

const cerrarPerfil = (e: MouseEvent) => {
  if (!(e.target as HTMLElement).closest('.perfil-wrapper')) {
    mostrarPerfil.value = false
  }
}
onMounted(() => document.addEventListener('click', cerrarPerfil))
onUnmounted(() => document.removeEventListener('click', cerrarPerfil))

const cambiarUsuario = async (id: string) => {
  await app.setUsuario(id)
  mostrarPerfil.value = false
}

const nombre = (u: any) => u.Nombre ?? u.Email ?? u.PK?.replace('USER#', '')
const direccionPorDefecto = (u: any) => u.Direcciones?.[0] ?? ''
const esActivo = (u: any) => u.PK === `USER#${app.usuarioId}`
</script>

<template>
  <header class="site-header">
    <div class="header-inner">
      <!-- Logo -->
      <div class="logo" @click="router.push('/')">
        Mi Mercado Global
      </div>

      <!-- Nav principal -->
      <nav class="main-nav">
        <RouterLink to="/">Inicio</RouterLink>
        <RouterLink to="/">Categorías</RouterLink>
        <RouterLink to="/">Ofertas</RouterLink>
        <RouterLink to="/">Marcas</RouterLink>
      </nav>

      <!-- Búsqueda -->
      <div class="search-box">
        <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
        </svg>
        <input
          v-model="busqueda"
          type="text"
          placeholder="Buscar productos..."
          class="search-input"
        />
      </div>

      <!-- Acciones -->
      <div class="header-actions">
        <!-- Carrito -->
        <button class="icon-btn" @click="app.cartAbierto = !app.cartAbierto">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/>
            <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>
          </svg>
          <span class="cart-label">Carrito</span>
          <span v-if="app.cantidadCarrito > 0" class="badge">{{ app.cantidadCarrito }}</span>
        </button>

        <!-- Perfil -->
        <div class="perfil-wrapper">
          <button class="icon-btn" @click.stop="mostrarPerfil = !mostrarPerfil">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
              <circle cx="12" cy="7" r="4"/>
            </svg>
          </button>

          <div v-if="mostrarPerfil" class="perfil-dropdown">
            <!-- Usuario activo -->
            <div v-if="app.usuarioPerfil" class="dropdown-bienvenida">
              <p class="bienvenida-titulo">
                Bienvenido, <strong>{{ app.usuarioPerfil.Nombre }}</strong>
              </p>
              <p class="bienvenida-dir">
                <span class="dir-label">Dirección de envío por defecto:</span><br/>
                {{ app.usuarioPerfil.Direcciones?.[0] ?? '—' }}
              </p>
            </div>

            <div class="dropdown-divider" />

            <!-- Lista de usuarios -->
            <p class="dropdown-seccion">Cambiar Perfil</p>
            <div
              v-for="u in usuarios"
              :key="u.PK"
              class="dropdown-user"
              :class="{ active: esActivo(u) }"
              @click="cambiarUsuario(u.PK.replace('USER#', ''))"
            >
              <div class="user-avatar-sm">{{ nombre(u).charAt(0) }}</div>
              <div class="user-meta">
                <div class="user-nombre">{{ nombre(u) }}</div>
                <div class="user-dir">{{ direccionPorDefecto(u) }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<style scoped>
.site-header {
  background: #1a73e8;
  color: #fff;
  padding: 0 2rem;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 8px rgba(0,0,0,.18);
}

.header-inner {
  max-width: 1280px;
  margin: 0 auto;
  height: 62px;
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.logo {
  font-weight: 700;
  font-size: 1.05rem;
  white-space: nowrap;
  cursor: pointer;
  letter-spacing: -.01em;
}

.main-nav {
  display: flex;
  gap: 1.25rem;
}
.main-nav a {
  color: rgba(255,255,255,.88);
  text-decoration: none;
  font-size: .9rem;
  white-space: nowrap;
  transition: color .12s;
}
.main-nav a:hover { color: #fff; }
.main-nav a.router-link-exact-active { color: #fff; font-weight: 600; }

/* Búsqueda */
.search-box {
  flex: 1;
  position: relative;
  max-width: 340px;
}
.search-icon {
  position: absolute;
  left: .75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #6e6e73;
  pointer-events: none;
}
.search-input {
  width: 100%;
  padding: .5rem .75rem .5rem 2.25rem;
  border: none;
  border-radius: 8px;
  font-size: .875rem;
  background: #fff;
  color: #1d1d1f;
  outline: none;
}
.search-input::placeholder { color: #9ca3af; }

/* Acciones */
.header-actions {
  display: flex;
  align-items: center;
  gap: .5rem;
  margin-left: auto;
}

.icon-btn {
  position: relative;
  background: rgba(255,255,255,.15);
  border: none;
  border-radius: 20px;
  padding: .4rem .85rem;
  display: flex;
  align-items: center;
  gap: .4rem;
  cursor: pointer;
  color: #fff;
  font-size: .875rem;
  transition: background .12s;
}
.icon-btn:hover { background: rgba(255,255,255,.25); }
.cart-label { white-space: nowrap; }

.badge {
  background: #ea4335;
  color: #fff;
  font-size: .7rem;
  font-weight: 700;
  border-radius: 10px;
  min-width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
}

/* Dropdown perfil */
.perfil-wrapper { position: relative; }

.perfil-dropdown {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  background: #fff;
  color: #1d1d1f;
  border-radius: 12px;
  box-shadow: 0 8px 28px rgba(0,0,0,.18);
  min-width: 270px;
  overflow: hidden;
  z-index: 200;
}

.dropdown-bienvenida {
  padding: 1rem 1.125rem .875rem;
}
.bienvenida-titulo {
  font-size: .9375rem;
  margin-bottom: .35rem;
}
.bienvenida-dir {
  font-size: .8125rem;
  color: #6e6e73;
  line-height: 1.4;
}
.dir-label { font-weight: 500; color: #1d1d1f; }

.dropdown-divider { height: 1px; background: #e8e8e8; }

.dropdown-seccion {
  padding: .5rem 1.125rem .25rem;
  font-size: .75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: .05em;
  color: #6e6e73;
}

.dropdown-user {
  display: flex;
  align-items: center;
  gap: .75rem;
  padding: .7rem 1.125rem;
  cursor: pointer;
  transition: background .1s;
}
.dropdown-user:hover  { background: #f5f5f7; }
.dropdown-user.active { background: #e8f0fe; }

.user-avatar-sm {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: #1a73e8;
  color: #fff;
  font-weight: 600;
  font-size: .9rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.user-nombre { font-size: .875rem; font-weight: 500; }
.user-dir    { font-size: .775rem; color: #6e6e73; margin-top: .1rem; }
</style>
