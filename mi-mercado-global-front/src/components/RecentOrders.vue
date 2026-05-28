<script setup>
import { ref, watch } from 'vue';

const props = defineProps(['usuarioId', 'seleccionado']);
const emit = defineEmits(['seleccionar']);
const pedidosData = ref([]);

watch(() => props.usuarioId, async (id) => {
  if (!id) return;
  try {
    const res = await fetch(`/api/usuarios/${id}/pedidos`);
    const data = await res.json();
    pedidosData.value = (data.pedidos ?? []).map(p => ({
      ...p,
      id_limpio: p.SK.split('#')[2]
    }));
  } catch (error) {
    console.error(error);
  }
}, { immediate: true });

const formatearFecha = (fechaISO) => {
  if(!fechaISO) return '';
  const fecha = new Date(fechaISO);
  return fecha.toLocaleDateString('es-CO', { year: 'numeric', month: '2-digit', day: '2-digit' });
};
</script>

<template>
  <div class="minimal-card orders-card">
    <div class="card-header">
      <h3>Pedidos Recientes</h3>
      <span class="count">{{ pedidosData.length }} pedidos</span>
    </div>
    <table class="minimal-table">
      <thead>
        <tr>
          <th>Estado</th>
          <th>Fecha Creación</th>
          <th>Dirección Envío</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="pedido in pedidosData" :key="pedido.id_limpio" 
            :class="{'selected-ref': pedido.id_limpio === props.seleccionado}"
            @click="emit('seleccionar', pedido.id_limpio)"
            style="cursor: pointer;">
          <td>
            <div class="status-cell">
              <span :class="['dot', {'dot-success': pedido.Estado === 'Pago exitoso', 'dot-pending': pedido.Estado === 'Enviado'}]"></span>
              {{ pedido.Estado }}
            </div>
          </td>
          <td>{{ formatearFecha(pedido.Fecha_Creacion) }}</td>
          <td>{{ pedido.Dir_Envio }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>