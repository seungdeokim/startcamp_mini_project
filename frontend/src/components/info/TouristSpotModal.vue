<script setup lang="ts">
import { X } from '@lucide/vue'
import type { TouristSpot } from '@/types/tourist'

defineProps<{
  spot: TouristSpot | null
}>()

const emit = defineEmits<{
  close: []
}>()
</script>

<template>
  <div v-if="spot" class="spot-modal__backdrop" @click.self="emit('close')">
    <div class="spot-modal">
      <button type="button" class="spot-modal__close" aria-label="닫기" @click="emit('close')">
        <X :size="18" />
      </button>

      <img v-if="spot.firstimage" :src="spot.firstimage" :alt="spot.title" class="spot-modal__image" />
      <div v-else class="spot-modal__image spot-modal__image--placeholder">이미지 없음</div>

      <h2 class="spot-modal__title">{{ spot.title }}</h2>
      <p class="spot-modal__row">{{ spot.addr1 }}{{ spot.addr2 ? ` ${spot.addr2}` : '' }}</p>
      <p v-if="spot.tel" class="spot-modal__row">{{ spot.tel }}</p>
    </div>
  </div>
</template>

<style scoped>
.spot-modal__backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 30;
  padding: 1rem;
}

.spot-modal {
  position: relative;
  background: var(--color-background);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  width: min(420px, 100%);
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: var(--shadow-lg);
}

.spot-modal__close {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  border: none;
  background: transparent;
  font-size: 1rem;
  color: var(--color-text-soft);
}

.spot-modal__image {
  width: 100%;
  height: 200px;
  object-fit: cover;
  border-radius: var(--radius-md);
  margin-bottom: 1rem;
  background: var(--color-background-mute);
}

.spot-modal__image--placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-soft);
  font-size: 0.85rem;
}

.spot-modal__title {
  font-size: 1.15rem;
  margin-bottom: 0.6rem;
}

.spot-modal__row {
  color: var(--color-text-soft);
  font-size: 0.9rem;
  margin-bottom: 0.3rem;
}
</style>
