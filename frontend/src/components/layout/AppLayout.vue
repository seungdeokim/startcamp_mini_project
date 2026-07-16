<script setup lang="ts">
import { computed } from 'vue'
import { RouterView, useRoute } from 'vue-router'
import AppHeader from './AppHeader.vue'
import BottomTabBar from './BottomTabBar.vue'
import ChatWidget from '@/components/chat/ChatWidget.vue'

const route = useRoute()
const isFullBleed = computed(() => Boolean(route.meta.fullBleed))
</script>

<template>
  <div class="app-layout">
    <AppHeader />
    <main class="app-layout__content" :class="{ 'app-layout__content--full-bleed': isFullBleed }">
      <RouterView />
    </main>
    <footer v-if="!isFullBleed" class="app-layout__footer">
      <p>© Gumi Log 교육 프로젝트 | 본 화면은 초안 와이어프레임입니다.</p>
    </footer>
    <BottomTabBar />
    <ChatWidget />
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

.app-layout__content--full-bleed {
  max-width: none;
  padding: 0;
  margin: 0;
}

.app-layout__footer {
  text-align: center;
  padding: 1.5rem;
  font-size: var(--text-xs);
  color: var(--color-text-soft);
  border-top: 1px solid var(--color-border);
}

@media (max-width: 480px) {
  .app-layout__content {
    padding: 1rem 0.85rem 2rem;
  }

  .app-layout__content--full-bleed {
    padding: 0;
  }
}

@media (max-width: 720px) {
  .app-layout__content:not(.app-layout__content--full-bleed) {
    padding-bottom: calc(3.5rem + env(safe-area-inset-bottom, 0px));
  }
}
</style>
