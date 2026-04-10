<script setup>
import { ref, onMounted } from 'vue';

const props = defineProps(['usuarioId', 'seleccionado']);
const emit = defineEmits(['seleccionar']);
const pedidosData = ref([]);

onMounted(async () => {
  try {
    const res = await fetch(`http://localhost:8001/api/usuarios/${props.usuarioId}/pedidos`);
    const data = await res.json();
    pedidosData.value = data.map(p => ({
      ...p,
      id_limpio: p.SK.split('#')[2]
    }));
  } catch (error) {
    console.error(error);
  }
});

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