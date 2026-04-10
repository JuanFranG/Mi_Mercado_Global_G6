<script setup>
import { ref, watch, onMounted } from 'vue';

const props = defineProps(['idPedido']);
const ordenData = ref(null);

const cargarDetalle = async (id) => {
  if (!id) return;
  try {
    const res = await fetch(`http://localhost:8001/api/pedidos/${id}`);
    ordenData.value = await res.json();
  } catch (error) {
    console.error(error);
  }
};

onMounted(() => cargarDetalle(props.idPedido));
watch(() => props.idPedido, (nuevoId) => cargarDetalle(nuevoId));

const formatearFechaHora = (fechaISO) => {
  if(!fechaISO) return '';
  const fecha = new Date(fechaISO);
  return fecha.toLocaleString('es-CO', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
};
</script>

<template>
  <div v-if="ordenData && ordenData.info.PK" class="minimal-card detail-panel">
    <h3>Detalle del Pedido ORD#{{ props.idPedido }}</h3>
    <div class="detail-section general-info">
      <h4>Información General</h4>
      <div class="info-grid">
        <div class="grid-item">
          <label>Fecha</label>
          <p>{{ formatearFechaHora(ordenData.info.Fecha_Creacion) }}</p>
        </div>
        <div class="grid-item">
          <label>Estado</label>
          <p class="status-text">{{ ordenData.info.Estado }}</p>
        </div>
        <div class="grid-item">
          <label>Total</label>
          <p class="total-text">${{ ordenData.info.Total }}</p>
        </div>
        <div class="grid-item">
          <label>Dirección</label>
          <p>{{ ordenData.info.Dir_Envio }}</p>
        </div>
      </div>
    </div>
    <div class="detail-section items-section">
      <h4>Ítems del Pedido</h4>
      <table class="minimal-table">
        <thead>
          <tr>
            <th>Ref.</th>
            <th>Producto</th>
            <th>Cantidad</th>
            <th>Precio Unitario</th>
            <th>Subtotal</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in ordenData.items" :key="index">
            <td class="ref-cell">{{ item.SK.split('#')[1] }}</td>
            <td>{{ item.Producto }}</td>
            <td>{{ item.Cantidad }}</td>
            <td>${{ item.Precio_Unitario_Compra }}</td>
            <td>${{ item.Subtotal }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>