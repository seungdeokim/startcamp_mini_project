<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { getTouristSpots } from '@/api/tourist'
import { getWeather } from '@/api/weather'
import { ApiError } from '@/api/client'
import { loadKakaoMaps } from '@/utils/kakaoMaps'
import { extractRegionFromAddress } from '@/utils/region'
import { calculateActivityIndex } from '@/utils/activityIndex'
import type { TouristSpot } from '@/types/tourist'
import type { WeatherInfo } from '@/types/weather'
import Pagination from '@/components/common/Pagination.vue'

const PAGE_SIZE = 15

const spots = ref<TouristSpot[]>([])
const isLoadingSpots = ref(true)
const spotsError = ref('')

const keyword = ref('')
const currentPage = ref(1)

const isKakaoReady = ref(false)
const mapError = ref('')
const isPanelOpen = ref(true)

const selectedSpot = ref<TouristSpot | null>(null)
const weather = ref<WeatherInfo | null>(null)
const isLoadingWeather = ref(false)
const weatherError = ref('')

const mapContainer = ref<HTMLDivElement | null>(null)
let mapInstance: any = null
let markerInstance: any = null

const activityIndex = computed(() => {
  if (!weather.value || weather.value.humidity === undefined) return null
  return calculateActivityIndex(weather.value.temp, weather.value.humidity, weather.value.weather)
})

async function loadSpots() {
  isLoadingSpots.value = true
  spotsError.value = ''
  try {
    spots.value = await getTouristSpots()
    const [firstSpot] = spots.value
    if (firstSpot) {
      selectedSpot.value = firstSpot
    }
  } catch (err) {
    spotsError.value = err instanceof ApiError ? err.message : '관광지 정보를 불러오지 못했습니다.'
  } finally {
    isLoadingSpots.value = false
  }
}

async function loadWeather(spot: TouristSpot) {
  isLoadingWeather.value = true
  weatherError.value = ''
  weather.value = null
  try {
    weather.value = await getWeather(extractRegionFromAddress(spot.addr1))
  } catch (err) {
    weatherError.value = err instanceof ApiError ? err.message : '날씨 정보를 불러오지 못했습니다.'
  } finally {
    isLoadingWeather.value = false
  }
}

function renderMap(spot: TouristSpot) {
  if (!mapContainer.value || !window.kakao?.maps) return

  const lat = parseFloat(spot.mapy) || 36.1194
  const lng = parseFloat(spot.mapx) || 128.3444
  const coords = new window.kakao.maps.LatLng(lat, lng)

  if (!mapInstance) {
    mapInstance = new window.kakao.maps.Map(mapContainer.value, { center: coords, level: 4 })
  } else {
    mapInstance.setCenter(coords)
  }

  if (!markerInstance) {
    markerInstance = new window.kakao.maps.Marker({ position: coords })
    markerInstance.setMap(mapInstance)
  } else {
    markerInstance.setPosition(coords)
  }
}

watch([selectedSpot, isKakaoReady], ([spot, ready]) => {
  if (spot && ready) {
    nextTick(() => renderMap(spot))
  }
})

watch(selectedSpot, (spot) => {
  if (spot) loadWeather(spot)
})

function selectSpot(spot: TouristSpot) {
  selectedSpot.value = spot
}

function handleSearch() {
  currentPage.value = 1
}

function handlePageChange(page: number) {
  currentPage.value = page
}

onMounted(() => {
  loadSpots()
  loadKakaoMaps()
    .then(() => {
      isKakaoReady.value = true
    })
    .catch((err) => {
      mapError.value = err instanceof Error ? err.message : '지도를 불러오지 못했습니다.'
    })
})

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
</script>

<template>
  <section class="map-page">
    <aside v-show="isPanelOpen" class="map-page__panel">
      <h1>지역정보 지도</h1>
      <p class="map-page__subtitle">관광지를 선택하면 위치와 현재 날씨를 볼 수 있어요</p>

      <input
        v-model="keyword"
        type="text"
        placeholder="관광지 이름이나 주소로 검색하세요"
        class="map-page__search"
        @keyup.enter="handleSearch"
      />

      <p v-if="isLoadingSpots" class="map-page__status">불러오는 중입니다...</p>
      <p v-else-if="spotsError" class="map-page__status map-page__status--error">{{ spotsError }}</p>
      <p v-else-if="pagedSpots.length === 0" class="map-page__status">검색 결과가 없습니다.</p>

      <ul v-else class="map-page__spot-list">
        <li v-for="spot in pagedSpots" :key="spot.contentid">
          <button
            type="button"
            class="map-page__spot-btn"
            :class="{ 'map-page__spot-btn--active': selectedSpot?.contentid === spot.contentid }"
            @click="selectSpot(spot)"
          >
            <span class="map-page__spot-title">{{ spot.title }}</span>
            <span class="map-page__spot-addr">{{ spot.addr1 }}</span>
          </button>
        </li>
      </ul>

      <Pagination :current-page="currentPage" :total-pages="totalPages" @change="handlePageChange" />
    </aside>

    <div class="map-page__map-area">
      <button
        type="button"
        class="map-page__panel-toggle"
        :aria-label="isPanelOpen ? '목록 숨기기' : '목록 보기'"
        @click="isPanelOpen = !isPanelOpen"
      >
        {{ isPanelOpen ? '‹ 목록' : '목록 ›' }}
      </button>

      <div class="map-page__map-wrap">
        <div ref="mapContainer" class="map-page__map"></div>
        <p v-if="mapError" class="map-page__map-error">{{ mapError }}</p>
      </div>

      <div v-if="selectedSpot" class="map-page__weather-card">
        <p class="map-page__weather-title">{{ selectedSpot.title }}</p>

        <p v-if="isLoadingWeather" class="map-page__status">날씨 정보를 불러오는 중...</p>
        <p v-else-if="weatherError" class="map-page__status map-page__status--error">{{ weatherError }}</p>

        <template v-else-if="weather">
          <div class="map-page__weather-grid">
            <div class="map-page__weather-cell">
              <span>기온</span>
              <strong>{{ weather.temp }}°C</strong>
            </div>
            <div class="map-page__weather-cell">
              <span>습도</span>
              <strong>{{ weather.humidity ?? '-' }}%</strong>
            </div>
            <div class="map-page__weather-cell">
              <span>날씨</span>
              <strong>{{ weather.weather }}</strong>
            </div>
          </div>

          <div v-if="activityIndex" class="map-page__activity" :class="`map-page__activity--${activityIndex.level}`">
            {{ activityIndex.text }}
          </div>
        </template>
      </div>
    </div>
  </section>
</template>

<style scoped>
.map-page {
  display: flex;
  gap: 1.25rem;
  height: calc(100vh - 160px);
  min-height: 480px;
}

.map-page__panel {
  width: 320px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.map-page__subtitle {
  color: var(--color-text-soft);
  font-size: 0.85rem;
  margin: 0.25rem 0 1rem;
}

.map-page__search {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: var(--color-background);
  color: var(--color-text);
  margin-bottom: 1rem;
}

.map-page__status {
  padding: 1.5rem 0;
  text-align: center;
  color: var(--color-text-soft);
  font-size: 0.85rem;
}

.map-page__status--error {
  color: var(--color-danger);
}

.map-page__spot-list {
  list-style: none;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  flex: 1;
  overflow-y: auto;
}

.map-page__spot-btn {
  width: 100%;
  text-align: left;
  padding: 0.6rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: var(--color-background);
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.map-page__spot-btn--active {
  border-color: var(--color-primary);
  background: var(--color-primary-soft);
}

.map-page__spot-title {
  font-weight: 600;
  font-size: 0.88rem;
}

.map-page__spot-addr {
  color: var(--color-text-soft);
  font-size: 0.75rem;
}

.map-page__map-area {
  flex: 1;
  min-width: 0;
  position: relative;
}

.map-page__panel-toggle {
  position: absolute;
  top: 1rem;
  left: 1rem;
  z-index: 5;
  padding: 0.5rem 0.85rem;
  min-height: 2.25rem;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: var(--color-background);
  color: var(--color-text);
  font-size: 0.8rem;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.map-page__map-wrap {
  position: absolute;
  inset: 0;
  border-radius: 12px;
  overflow: hidden;
  background: var(--color-background-mute);
}

.map-page__map {
  width: 100%;
  height: 100%;
}

.map-page__map-error {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-soft);
  padding: 1rem;
  text-align: center;
}

.map-page__weather-card {
  position: absolute;
  top: 1rem;
  right: 1rem;
  z-index: 5;
  width: min(260px, calc(100% - 2rem));
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 1rem;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.map-page__weather-title {
  font-weight: 700;
  font-size: 0.9rem;
  margin-bottom: 0.6rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.map-page__weather-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
  margin-bottom: 0.6rem;
}

.map-page__weather-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.15rem;
  background: var(--color-background-soft);
  border-radius: 8px;
  padding: 0.5rem 0.3rem;
  font-size: 0.75rem;
}

.map-page__weather-cell span {
  color: var(--color-text-soft);
}

.map-page__activity {
  text-align: center;
  border-radius: 8px;
  padding: 0.5rem;
  font-size: 0.8rem;
  font-weight: 700;
  border: 1px solid transparent;
}

.map-page__activity--danger {
  color: var(--color-danger);
  background: var(--color-danger-soft);
  border-color: var(--color-danger);
}

.map-page__activity--warning {
  color: var(--color-warning);
  background: var(--color-warning-soft);
  border-color: var(--color-warning);
}

.map-page__activity--info {
  color: var(--color-info);
  background: var(--color-info-soft);
  border-color: var(--color-info);
}

.map-page__activity--success {
  color: var(--color-success);
  background: var(--color-success-soft);
  border-color: var(--color-success);
}

@media (max-width: 720px) {
  .map-page {
    flex-direction: column;
    height: auto;
  }

  .map-page__panel {
    width: 100%;
    max-height: 320px;
  }

  .map-page__map-area {
    height: 420px;
  }
}
</style>
