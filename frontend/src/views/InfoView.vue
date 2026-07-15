<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { getTouristSpots } from '@/api/tourist'
import { ApiError } from '@/api/client'
import type { TouristSpot } from '@/types/tourist'
import Pagination from '@/components/common/Pagination.vue'
import TouristSpotModal from '@/components/info/TouristSpotModal.vue'

const PAGE_SIZE = 12

const spots = ref<TouristSpot[]>([])
const isLoading = ref(true)
const errorMessage = ref('')
const keyword = ref('')
const currentPage = ref(1)
const selectedSpot = ref<TouristSpot | null>(null)

async function loadSpots() {
  isLoading.value = true
  errorMessage.value = ''
  try {
    spots.value = await getTouristSpots()
  } catch (err) {
    errorMessage.value = err instanceof ApiError ? err.message : '지역정보를 불러오지 못했습니다.'
  } finally {
    isLoading.value = false
  }
}

onMounted(loadSpots)

const filteredSpots = computed(() => {
  const keywordTrimmed = keyword.value.trim().toLowerCase()
  if (!keywordTrimmed) return spots.value
  return spots.value.filter(
    (spot) => spot.title.toLowerCase().includes(keywordTrimmed) || spot.addr1.toLowerCase().includes(keywordTrimmed),
  )
})

const totalPages = computed(() => Math.max(1, Math.ceil(filteredSpots.value.length / PAGE_SIZE)))

const pagedSpots = computed(() => {
  const start = (currentPage.value - 1) * PAGE_SIZE
  return filteredSpots.value.slice(start, start + PAGE_SIZE)
})

function handleSearch() {
  currentPage.value = 1
}

function handlePageChange(page: number) {
  currentPage.value = page
}
</script>

<template>
  <section class="info">
    <h1>지역정보</h1>
    <p class="info__subtitle">구미/경북 권역의 관광지 정보를 확인해보세요</p>

    <div class="info__toolbar">
      <input
        v-model="keyword"
        type="text"
        placeholder="관광지 이름이나 주소로 검색하세요"
        class="info__search"
        @keyup.enter="handleSearch"
      />
      <button type="button" class="info__search-btn" @click="handleSearch">검색</button>
    </div>

    <p v-if="isLoading" class="info__status">불러오는 중입니다...</p>
    <p v-else-if="errorMessage" class="info__status info__status--error">{{ errorMessage }}</p>
    <p v-else-if="pagedSpots.length === 0" class="info__status">검색 결과가 없습니다.</p>

    <div v-else class="info__grid">
      <button
        v-for="spot in pagedSpots"
        :key="spot.contentid"
        type="button"
        class="info__card"
        @click="selectedSpot = spot"
      >
        <img v-if="spot.firstimage" :src="spot.firstimage" :alt="spot.title" class="info__card-image" />
        <div v-else class="info__card-image info__card-image--placeholder">이미지 없음</div>
        <div class="info__card-body">
          <p class="info__card-title">{{ spot.title }}</p>
          <p class="info__card-addr">{{ spot.addr1 }}</p>
        </div>
      </button>
    </div>

    <Pagination :current-page="currentPage" :total-pages="totalPages" @change="handlePageChange" />

    <TouristSpotModal :spot="selectedSpot" @close="selectedSpot = null" />
  </section>
</template>

<style scoped>
.info__subtitle {
  color: var(--color-text-soft);
  margin: 0.25rem 0 1.25rem;
}

.info__toolbar {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.25rem;
}

.info__search {
  font-size: 0.7rem;
  flex: 1;
  padding: 0.6rem 1rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-full);
  background: var(--color-background);
  color: var(--color-text);
}

.info__search-btn {
  padding: 0.6rem 1.1rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-full);
  background: var(--color-background);
  font-weight: 600;
}

.info__status {
  padding: 2rem 0;
  text-align: center;
  color: var(--color-text-soft);
}

.info__status--error {
  color: var(--color-danger);
}

.info__grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}

@media (max-width: 720px) {
  .info__grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.info__card {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: var(--color-background);
  text-align: left;
  padding: 0;
  box-shadow: var(--shadow-sm);
  transition: transform 0.15s ease;
}

.info__card:hover {
  transform: translateY(-2px);
  border-color: var(--color-primary);
}

.info__card-image {
  width: 100%;
  height: 110px;
  object-fit: cover;
  background: var(--color-background-mute);
  display: block;
}

.info__card-image--placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-soft);
  font-size: 0.75rem;
}

.info__card-body {
  padding: 0.6rem 0.7rem;
}

.info__card-title {
  font-weight: 600;
  font-size: 0.9rem;
  margin-bottom: 0.25rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.info__card-addr {
  color: var(--color-text-soft);
  font-size: 0.78rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
