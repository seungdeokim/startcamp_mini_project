<script setup lang="ts">
import { onBeforeUnmount, onMounted } from 'vue'
import { X, MapPin, Phone } from '@lucide/vue'
import type { TouristSpot } from '@/types/tourist'

const props = defineProps<{
  spot: TouristSpot | null
}>()

const emit = defineEmits<{
  close: []
}>()

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape' && props.spot) emit('close')
}

onMounted(() => window.addEventListener('keydown', handleKeydown))
onBeforeUnmount(() => window.removeEventListener('keydown', handleKeydown))

function fullAddress(spot: TouristSpot) {
  return `${spot.addr1}${spot.addr2 ? ` ${spot.addr2}` : ''}`.trim()
}

function mapLink(spot: TouristSpot) {
  return `https://map.kakao.com/link/map/${encodeURIComponent(spot.title)},${spot.mapy},${spot.mapx}`
}
</script>

<template>
  <Transition name="spot-modal">
    <div v-if="spot" class="spot-modal__backdrop" @click.self="emit('close')">
      <div class="spot-modal" role="dialog" aria-modal="true">
        <div class="spot-modal__media">
          <img v-if="spot.firstimage" :src="spot.firstimage" :alt="spot.title" class="spot-modal__image" />
          <div v-else class="spot-modal__image spot-modal__image--placeholder">
            <MapPin :size="34" :stroke-width="1.6" />
            <span>이미지 준비 중</span>
          </div>

          <span class="spot-modal__badge">구미 · 경북 관광지</span>

          <button type="button" class="spot-modal__close" aria-label="닫기" @click="emit('close')">
            <X :size="18" :stroke-width="2.5" />
          </button>

          <div class="spot-modal__media-caption">
            <h2 class="spot-modal__title">{{ spot.title }}</h2>
          </div>
        </div>

        <div class="spot-modal__body">
          <div class="spot-modal__row">
            <span class="spot-modal__row-icon"><MapPin :size="16" :stroke-width="2.2" /></span>
            <span class="spot-modal__row-text">{{ fullAddress(spot) }}</span>
          </div>
          <div v-if="spot.tel" class="spot-modal__row">
            <span class="spot-modal__row-icon"><Phone :size="16" :stroke-width="2.2" /></span>
            <span class="spot-modal__row-text">{{ spot.tel }}</span>
          </div>

          <a :href="mapLink(spot)" target="_blank" rel="noopener" class="spot-modal__cta">
            <MapPin :size="16" :stroke-width="2.5" />
            카카오맵에서 길찾기
          </a>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.spot-modal__backdrop {
  position: fixed;
  inset: 0;
  background: rgba(20, 20, 20, 0.55);
  backdrop-filter: blur(3px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
  padding: 1rem;
}

.spot-modal {
  position: relative;
  background: var(--color-background);
  border-radius: var(--radius-xl);
  width: min(420px, 100%);
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: var(--shadow-lg);
}

.spot-modal__media {
  position: relative;
  height: 220px;
}

.spot-modal__image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  background: var(--color-background-mute);
  display: block;
}

.spot-modal__image--placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  color: #fff;
  font-size: var(--text-sm);
  font-weight: var(--weight-semibold);
  background: var(--gradient-brand);
}

.spot-modal__badge {
  position: absolute;
  top: 0.9rem;
  left: 0.9rem;
  background: rgba(255, 255, 255, 0.9);
  color: var(--color-primary-hover);
  font-size: var(--text-xs);
  font-weight: var(--weight-bold);
  padding: 0.3rem 0.7rem;
  border-radius: var(--radius-full);
  backdrop-filter: blur(4px);
}

.spot-modal__close {
  position: absolute;
  top: 0.9rem;
  right: 0.9rem;
  width: 34px;
  height: 34px;
  border-radius: var(--radius-full);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-heading);
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(4px);
  cursor: pointer;
  transition: transform 0.15s ease;
}

.spot-modal__close:hover {
  transform: rotate(90deg);
}

.spot-modal__media-caption {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 2rem 1.25rem 0.9rem;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.72), rgba(0, 0, 0, 0));
}

.spot-modal__title {
  color: #fff;
  font-size: var(--text-lg);
  font-weight: var(--weight-extrabold);
  letter-spacing: -0.02em;
  text-shadow: 0 1px 6px rgba(0, 0, 0, 0.4);
}

.spot-modal__body {
  padding: 1.1rem 1.25rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.spot-modal__row {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
}

.spot-modal__row-icon {
  flex-shrink: 0;
  width: 30px;
  height: 30px;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary);
  background: var(--color-primary-soft);
}

.spot-modal__row-text {
  font-size: var(--text-sm);
  color: var(--color-text);
  line-height: 1.5;
  padding-top: 0.35rem;
}

.spot-modal__cta {
  margin-top: 0.4rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  padding: 0.75rem;
  border-radius: var(--radius-md);
  background: var(--color-primary);
  color: #fff;
  font-size: var(--text-sm);
  font-weight: var(--weight-bold);
  text-decoration: none;
  transition:
    background 0.15s ease,
    transform 0.15s ease;
}

.spot-modal__cta:hover {
  background: var(--color-primary-hover);
  text-decoration: none;
  transform: translateY(-1px);
}

/* 등장/퇴장 애니메이션 */
.spot-modal-enter-active,
.spot-modal-leave-active {
  transition: opacity 0.2s ease;
}

.spot-modal-enter-active .spot-modal,
.spot-modal-leave-active .spot-modal {
  transition:
    transform 0.24s cubic-bezier(0.32, 0.72, 0, 1),
    opacity 0.24s ease;
}

.spot-modal-enter-from,
.spot-modal-leave-to {
  opacity: 0;
}

.spot-modal-enter-from .spot-modal,
.spot-modal-leave-to .spot-modal {
  opacity: 0;
  transform: translateY(24px) scale(0.97);
}
</style>
