<script setup lang="ts">
import { RouterLink, useRoute } from 'vue-router'
import { Home, NotebookText, MapPin, Map } from '@lucide/vue'

const route = useRoute()

const tabs = [
  { to: '/', label: '홈', icon: Home },
  { to: '/board', label: '게시판', icon: NotebookText },
  { to: '/info', label: '지역정보', icon: MapPin },
  { to: '/map', label: '지도', icon: Map },
]
</script>

<template>
  <nav class="bottom-tab-bar">
    <RouterLink
      v-for="tab in tabs"
      :key="tab.to"
      :to="tab.to"
      class="bottom-tab-bar__item"
      :class="{ 'bottom-tab-bar__item--active': route.path === tab.to }"
    >
      <component :is="tab.icon" class="bottom-tab-bar__icon" :size="22" :stroke-width="2" />
      <span class="bottom-tab-bar__label">{{ tab.label }}</span>
    </RouterLink>
  </nav>
</template>

<style scoped>
.bottom-tab-bar {
  display: none;
}

@media (max-width: 720px) {
  .bottom-tab-bar {
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 40;
    display: flex;
    background: var(--color-background);
    box-shadow: 0 -2px 12px rgba(33, 37, 41, 0.08);
    padding-bottom: env(safe-area-inset-bottom, 0);
  }
}

.bottom-tab-bar__item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.15rem;
  padding: 0.5rem 0 0.6rem;
  color: var(--color-text-soft);
  text-decoration: none;
}

.bottom-tab-bar__icon {
  display: block;
}

.bottom-tab-bar__label {
  font-size: 0.68rem;
  font-weight: 600;
}

.bottom-tab-bar__item--active {
  color: var(--color-primary);
}
</style>
