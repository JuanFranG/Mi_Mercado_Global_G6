import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAppStore = defineStore('app', () => {
  const usuarioId     = ref('550e8400-e29b-41d4-a716-446655440000')
  const usuarioPerfil = ref<any>(null)
  const carritoItems  = ref<any[]>([])
  const cartAbierto   = ref(false)
  const searchQuery   = ref('')
  const pedidoCreado  = ref<string | null>(null)

  const cantidadCarrito = computed(() =>
    carritoItems.value.reduce((s, i) => s + i.cantidad, 0)
  )
  const totalCarrito = computed(() =>
    carritoItems.value.reduce((s, i) => s + i.precio * i.cantidad, 0)
  )

  async function cargarPerfil() {
    try {
      const res  = await fetch(`/api/usuarios/${usuarioId.value}/perfil`)
      const data = await res.json()
      usuarioPerfil.value = data
    } catch { usuarioPerfil.value = null }
  }

  async function setUsuario(id: string) {
    usuarioId.value     = id
    usuarioPerfil.value = null
    await Promise.all([cargarPerfil(), cargarCarrito()])
  }

  async function cargarCarrito() {
    try {
      const res  = await fetch(`/api/carrito/${usuarioId.value}`)
      const data = await res.json()
      carritoItems.value = data.items ?? []
    } catch { carritoItems.value = [] }
  }

  async function agregarAlCarrito(item: {
    producto_id: string; nombre: string; precio: number; cantidad: number
  }) {
    const res  = await fetch(`/api/carrito/${usuarioId.value}/items`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(item),
    })
    const data = await res.json()
    carritoItems.value = data.items ?? []
    cartAbierto.value  = true
  }

  async function eliminarDelCarrito(productoId: string) {
    const res  = await fetch(
      `/api/carrito/${usuarioId.value}/items/${encodeURIComponent(productoId)}`,
      { method: 'DELETE' }
    )
    const data = await res.json()
    carritoItems.value = data.items ?? []
  }

  async function limpiarCarrito() {
    await fetch(`/api/carrito/${usuarioId.value}`, { method: 'DELETE' })
    carritoItems.value = []
  }

  async function realizarPedido() {
    const dirEnvio = usuarioPerfil.value?.Direcciones?.[0] ?? 'Dirección por defecto'
    const res = await fetch('/api/pedidos', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({
        usuario_id: usuarioId.value,
        items:      carritoItems.value,
        dir_envio:  dirEnvio,
        total:      totalCarrito.value,
      }),
    })
    const data = await res.json()
    carritoItems.value = []
    cartAbierto.value  = false
    pedidoCreado.value = data.id_pedido
    setTimeout(() => { pedidoCreado.value = null }, 4000)
    return data
  }

  return {
    usuarioId, usuarioPerfil, carritoItems, cartAbierto,
    searchQuery, pedidoCreado,
    cantidadCarrito, totalCarrito,
    cargarPerfil, setUsuario, cargarCarrito,
    agregarAlCarrito, eliminarDelCarrito, limpiarCarrito, realizarPedido,
  }
})
