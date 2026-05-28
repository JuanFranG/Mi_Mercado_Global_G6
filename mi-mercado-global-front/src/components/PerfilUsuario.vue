<script setup>
import { ref } from 'vue'

const perfil = ref({
  nombre: 'Luisa',
  email: 'luisa@x.com',
  direcciones: ['Calle 10, Bogotá', 'Ave 5, Medellín'],
  pagos: ['Visa **** 1234', 'Paypal'],
})
</script>

<template>
  <div class="glass-card profile-wrapper">
    <div class="avatar">
      {{ perfil.nombre.charAt(0) }}
    </div>

    <div class="user-id">
      <h2>{{ perfil.nombre }}</h2>
      <p>{{ perfil.email }}</p>
    </div>

    <div class="data-block">
      <h3>Direcciones</h3>
      <ul>
        <li v-for="(dir, index) in perfil.direcciones" :key="index">{{ dir }}</li>
      </ul>
    </div>

    <div class="data-block">
      <h3>Métodos de Pago</h3>
      <ul>
        <li v-for="(pago, index) in perfil.pagos" :key="index">{{ pago }}</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.profile-wrapper {
  padding: 2rem 1.5rem;
}

.avatar {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  background: var(--text-main);
  color: var(--bg-base);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  font-weight: 500;
  margin-bottom: 1.5rem;
}

.user-id {
  margin-bottom: 2.5rem;
}

.user-id h2 {
  font-size: 1rem;
}

.user-id p {
  color: var(--text-muted);
  font-size: 0.875rem;
}

.data-block {
  margin-bottom: 2rem;
}

.data-block:last-child {
  margin-bottom: 0;
}

.data-block h3 {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  margin-bottom: 0.75rem;
}

ul {
  list-style: none;
}

li {
  font-size: 0.875rem;
  color: var(--text-main);
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--border-subtle);
}

li:last-child {
  border-bottom: none;
}
</style>
