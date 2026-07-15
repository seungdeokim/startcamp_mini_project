<script setup lang="ts">
import { RouterView } from 'vue-router'
import AppHeader from './AppHeader.vue'
</script>

<template>
  <div class="app-layout">
    <AppHeader />
    <main class="app-layout__content">
      <RouterView />
    </main>
    <footer class="app-layout__footer">
      <p>© LocalHub 교육 프로젝트 | 본 화면은 초안 와이어프레임입니다.</p>
    </footer>
  </div>
</template>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-layout__content {
  flex: 1;
  width: 100%;
  max-width: 960px;
  margin: 0 auto;
  padding: 1.5rem 1.25rem 3rem;
}

.app-layout__footer {
  text-align: center;
  padding: 1.5rem;
  font-size: 0.8rem;
  color: var(--color-text-soft);
  border-top: 1px solid var(--color-border);
}

@media (max-width: 480px) {
  .app-layout__content {
    padding: 1rem 0.85rem 2rem;
  }
}
</style>
