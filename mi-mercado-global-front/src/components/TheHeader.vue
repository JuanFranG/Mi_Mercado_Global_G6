<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

const fechaHoraReal = ref('');
let intervaloTiempo;

const actualizarTiempo = () => {
  const ahora = new Date();
  
  const fechaStr = ahora.toLocaleDateString('es-CO', { 
    day: 'numeric', 
    month: 'long' 
  });
  
  const horaStr = ahora.toLocaleTimeString('es-CO', { 
    hour: '2-digit', 
    minute: '2-digit',
    hour12: false
  });

  fechaHoraReal.value = `${fechaStr}, ${horaStr}`;
};

onMounted(() => {
  actualizarTiempo();
  intervaloTiempo = setInterval(actualizarTiempo, 60000);
});

onUnmounted(() => {
  clearInterval(intervaloTiempo);
});
</script>

<template>
  <header class="main-header">
    <div class="header-content">
      <div class="header-left">
        <h1>Mi Mercado Global</h1>
        <p>Panel de Control</p>
      </div>
      <div class="header-right">
        <nav class="breadcrumb">
          <span>Inicio</span>
          <span class="sep">/</span>
          <span>Usuario</span>
          <span class="sep">/</span>
          <span class="active">Luisa</span>
          <span class="sep">/</span>
          <span class="active">Pedidos Recientes</span>
        </nav>
        <div class="timestamp">
          {{ fechaHoraReal }}
        </div>
      </div>
    </div>
  </header>
</template>

<style scoped>
.main-header {
  border-bottom: 1px solid var(--border-muted);
  background: var(--bg-base);
  padding: 1.25rem 2rem;
}

.header-content {
  max-width: 1240px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-left h1 {
  font-size: 1.125rem;
}

.panel-tag {
  color: var(--text-muted);
  font-size: 0.8125rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 0.25rem 0.5rem;
  border: 1px solid var(--border-strong);
  border-radius: 4px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 2rem;
  font-size: 0.8125rem;
}

.breadcrumb {
  display: flex;
  gap: 0.5rem;
  color: var(--text-muted);
}

.breadcrumb .active {
  color: var(--accent);
}

.timestamp {
  color: var(--text-muted);
  padding: 0.25rem 0.75rem;
  background: rgba(0,0,0,0.03);
  border-radius: 20px;
}
</style>