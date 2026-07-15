<script setup lang="ts">
import { computed } from 'vue'

const WINDOW_SIZE = 5

const props = defineProps<{
  currentPage: number
  totalPages: number
}>()

const emit = defineEmits<{
  change: [page: number]
}>()

const windowStart = computed(() => Math.floor((props.currentPage - 1) / WINDOW_SIZE) * WINDOW_SIZE + 1)
const windowEnd = computed(() => Math.min(windowStart.value + WINDOW_SIZE - 1, props.totalPages))
const pages = computed(() =>
  Array.from({ length: windowEnd.value - windowStart.value + 1 }, (_, i) => windowStart.value + i),
)

function go(page: number) {
  if (page < 1 || page > props.totalPages || page === props.currentPage) return
  emit('change', page)
}

function goPrevBlock() {
  if (windowStart.value > 1) go(windowStart.value - 1)
}

function goNextBlock() {
  if (windowEnd.value < props.totalPages) go(windowEnd.value + 1)
}
</script>

<template>
  <nav v-if="totalPages > 1" class="pagination" aria-label="페이지네이션">
    <button type="button" class="pagination__arrow" :disabled="windowStart === 1" @click="goPrevBlock">&lt;</button>
    <button
      v-for="page in pages"
      :key="page"
      type="button"
      class="pagination__page"
      :class="{ 'pagination__page--active': page === currentPage }"
      @click="go(page)"
    >
      {{ page }}
    </button>
    <button type="button" class="pagination__arrow" :disabled="windowEnd === totalPages" @click="goNextBlock">
      &gt;
    </button>
  </nav>
</template>

<style scoped>
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.35rem;
  margin-top: 1.5rem;
}

.pagination__page,
.pagination__arrow {
  min-width: 2rem;
  height: 2rem;
  border: 1px solid var(--color-border);
  background: var(--color-background);
  border-radius: 6px;
  color: var(--color-text);
  font-size: 0.85rem;
}

.pagination__page--active {
  border-color: var(--color-primary);
  color: var(--color-primary);
  font-weight: 700;
}

.pagination__arrow:disabled {
  opacity: 0.4;
  cursor: default;
}
</style>
