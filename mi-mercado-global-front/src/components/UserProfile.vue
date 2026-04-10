<script setup>
import { ref, onMounted } from 'vue';

const props = defineProps(['usuarioId']);
const perfilData = ref(null);

onMounted(async () => {
  try {
    const res = await fetch(`http://localhost:8001/api/usuarios/${props.usuarioId}/perfil`);
    perfilData.value = await res.json();
  } catch (error) {
    console.error(error);
  }
});
</script>

<template>
  <div v-if="perfilData" class="minimal-card profile-card">
    <h3>Mi Perfil</h3>
    
    <div class="profile-header">
      <div class="avatar-ref">
        {{ perfilData.Nombre?.charAt(0) }}
      </div>
      <div class="profile-meta">
        <h2>{{ perfilData.Nombre }}</h2>
        <p>{{ perfilData.Email }}</p>
      </div>
    </div>

    <div class="info-group">
      <h4>Direcciones</h4>
      <div v-for="(dir, index) in perfilData.Direcciones" :key="index" class="info-item">
        {{ dir }}
      </div>
    </div>

    <div class="info-group">
      <h4>Pagos</h4>
      <div v-for="(pago, index) in perfilData.Metodos_Pago" :key="index" class="info-item payment-item">
        {{ pago }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-card h3 {
  color: var(--text-muted);
  font-size: 0.8125rem;
  text-transform: uppercase;
  margin-bottom: 1.5rem;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  margin-bottom: 2rem;
}

.avatar-ref {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--text-main);
  color: var(--bg-base);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 500;
}

.profile-meta h2 {
  font-size: 1.125rem;
}

.profile-meta p {
  color: var(--text-muted);
  font-size: 0.875rem;
}

.info-group {
  margin-top: 1.5rem;
}

.info-group h4 {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  margin-bottom: 0.75rem;
}

.info-item {
 
  padding: 0.5rem 0;
  font-size: 0.875rem;
  color: var(--text-main);
  border-bottom: 1px solid var(--border-muted);
}

.info-item:last-child {
  border-bottom: none;
}
</style>