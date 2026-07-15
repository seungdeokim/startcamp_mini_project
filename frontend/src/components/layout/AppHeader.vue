<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <header class="app-header">
    <div class="app-header__inner">
      <RouterLink to="/" class="app-header__brand">LocalHub</RouterLink>
      <nav class="app-header__nav">
        <RouterLink to="/board">게시판</RouterLink>
        <RouterLink to="/info">지역정보</RouterLink>
        <RouterLink to="/map">지도</RouterLink>
      </nav>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  position: sticky;
  top: 0;
  z-index: 20;
  background: var(--color-background);
  box-shadow: var(--shadow-sm);
}

.app-header__inner {
  max-width: 960px;
  margin: 0 auto;
  padding: 0.9rem 1.25rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.app-header__brand {
  font-size: 1.2rem;
  font-weight: 800;
  color: var(--color-primary);
  text-decoration: none;
}

.app-header__nav {
  display: flex;
  gap: 0.35rem;
}

.app-header__nav a {
  color: var(--color-text-soft);
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 600;
  padding: 0.4rem 0.85rem;
  border-radius: var(--radius-full);
}

.app-header__nav a.router-link-active {
  color: var(--color-heading);
  background: var(--color-background-soft);
}

@media (max-width: 720px) {
  .app-header__nav {
    display: none;
  }
}
</style>
