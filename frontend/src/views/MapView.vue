<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { getTouristSpots } from '@/api/tourist'
import { getWeather } from '@/api/weather'
import { ApiError } from '@/api/client'
import { loadKakaoMaps } from '@/utils/kakaoMaps'
import { extractRegionFromAddress } from '@/utils/region'
import { calculateActivityIndex } from '@/utils/activityIndex'
import { createMarkerImage } from '@/utils/kakaoMarkerImage'
import type { TouristSpot } from '@/types/tourist'
import type { WeatherInfo } from '@/types/weather'
import { Search, ChevronLeft, MapPin } from '@lucide/vue'

// 날씨 배지 지역 한글 라벨(백엔드가 영문 region을 그대로 echo하므로 매핑해서 보여준다).
const REGION_LABELS: Record<string, string> = {
  Gumi: '구미',
  Daegu: '대구',
  Gimcheon: '김천',
  Sangju: '상주',
  Chilgok: '칠곡',
}

// 클러스터 배지 스타일: 개수 구간(10 미만/10~49/50 이상)에 따라 커지는 3단계.
// 마커와 톤을 맞추기 위해 브랜드 오렌지 대신 중립 톤(검정 반투명)을 사용한다.
const CLUSTER_STYLES = [
  {
    width: '34px',
    height: '34px',
    background: 'rgba(33, 37, 41, 0.9)',
    borderRadius: '17px',
    color: '#ffffff',
    textAlign: 'center',
    lineHeight: '34px',
    fontWeight: '700',
    fontSize: '12px',
    border: '2px solid #ffffff',
    boxShadow: '0 3px 10px rgba(0, 0, 0, 0.25)',
  },
  {
    width: '44px',
    height: '44px',
    background: 'rgba(33, 37, 41, 0.92)',
    borderRadius: '22px',
    color: '#ffffff',
    textAlign: 'center',
    lineHeight: '44px',
    fontWeight: '700',
    fontSize: '13px',
    border: '3px solid #ffffff',
    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.28)',
  },
  {
    width: '54px',
    height: '54px',
    background: 'rgba(33, 37, 41, 0.94)',
    borderRadius: '27px',
    color: '#ffffff',
    textAlign: 'center',
    lineHeight: '54px',
    fontWeight: '700',
    fontSize: '14px',
    border: '3px solid #ffffff',
    boxShadow: '0 5px 14px rgba(0, 0, 0, 0.3)',
  },
]

const spots = ref<TouristSpot[]>([])
const isLoadingSpots = ref(true)
const spotsError = ref('')

const keyword = ref('')

const isKakaoReady = ref(false)
const mapError = ref('')

const selectedSpot = ref<TouristSpot | null>(null)
const weather = ref<WeatherInfo | null>(null)
const isLoadingWeather = ref(false)
const weatherError = ref('')

const isSheetExpanded = ref(false)

const mapContainer = ref<HTMLDivElement | null>(null)
let mapInstance: any = null
let clusterer: any = null
const markerRegistry = new Map<string, any>()
let renderMarkersTimer: ReturnType<typeof setTimeout> | null = null
let touchStartY = 0

// 클러스터로 묶이지 않은 개별 마커마다 항상 떠 있는 "이름만" 라벨.
const nameLabelRegistry = new Map<string, any>()

// 마커 hover/click 시 뜨는 "사진+이름" 정보 카드(Overlay). 카드 하나를 재사용해 위치/내용만 바꾼다.
let infoOverlay: any = null
let infoOverlayEl: HTMLDivElement | null = null
let isOverlayPinned = false
// 정보 카드가 떠 있는 대상 스팟(hover 중이든 pin 되었든). 이 스팟의 이름 라벨은 카드와 겹치지 않도록 숨긴다.
let activeSpotId: string | null = null

const activityIndex = computed(() => {
  if (!weather.value || weather.value.humidity === undefined) return null
  return calculateActivityIndex(weather.value.temp, weather.value.humidity, weather.value.weather)
})

const filteredSpots = computed(() => {
  const keywordTrimmed = keyword.value.trim().toLowerCase()
  if (!keywordTrimmed) return spots.value
  return spots.value.filter(
    (spot) =>
      spot.title.toLowerCase().includes(keywordTrimmed) ||
      spot.addr1.toLowerCase().includes(keywordTrimmed),
  )
})

// 두 좌표 간 거리(km) — Haversine 공식.
function distanceKm(aLat: number, aLng: number, bLat: number, bLng: number): number {
  const R = 6371
  const dLat = ((bLat - aLat) * Math.PI) / 180
  const dLng = ((bLng - aLng) * Math.PI) / 180
  const s =
    Math.sin(dLat / 2) ** 2 +
    Math.cos((aLat * Math.PI) / 180) * Math.cos((bLat * Math.PI) / 180) * Math.sin(dLng / 2) ** 2
  return 2 * R * Math.asin(Math.sqrt(s))
}

// 선택된 관광지 기준 가까운 순 최대 4곳(자기 자신 제외). 검색어와 무관하게 전체에서 추천한다.
const nearbySpots = computed(() => {
  const s = selectedSpot.value
  if (!s) return []
  const lat = parseFloat(s.mapy)
  const lng = parseFloat(s.mapx)
  if (!lat || !lng) return []
  return spots.value
    .filter((o) => o.contentid !== s.contentid && parseFloat(o.mapy) && parseFloat(o.mapx))
    .map((o) => ({ spot: o, dist: distanceKm(lat, lng, parseFloat(o.mapy), parseFloat(o.mapx)) }))
    .sort((a, b) => a.dist - b.dist)
    .slice(0, 4)
})

function formatDistance(km: number): string {
  return km < 1 ? `${Math.round(km * 1000)}m` : `${km.toFixed(1)}km`
}

const weatherRegionLabel = computed(() =>
  weather.value ? (REGION_LABELS[weather.value.region] ?? weather.value.region) : '',
)

async function loadSpots() {
  isLoadingSpots.value = true
  spotsError.value = ''
  try {
    spots.value = await getTouristSpots()
  } catch (err) {
    spotsError.value = err instanceof ApiError ? err.message : '관광지 정보를 불러오지 못했습니다.'
  } finally {
    isLoadingSpots.value = false
  }
}

async function loadWeather(region: string) {
  isLoadingWeather.value = true
  weatherError.value = ''
  try {
    weather.value = await getWeather(region)
  } catch (err) {
    weatherError.value = err instanceof ApiError ? err.message : '날씨 정보를 불러오지 못했습니다.'
  } finally {
    isLoadingWeather.value = false
  }
}

function escapeHtml(text: string) {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

// 마커/카드 클릭이 지도 자체의 click으로도 버블링되어 클릭 직후 곧바로
// closePinnedOverlay()가 실행되는 것을 막기 위한 가드. 카카오는 클릭 한 번에
// 지도 click 이벤트를 시차를 두고 여러 번 발생시킬 수 있어(확대/이동 애니메이션과 맞물림),
// 한 번 쓰면 소진되는 boolean 플래그로는 두 번째 이후 발생을 못 막는다.
// 그래서 "마지막 마커/카드 상호작용 시각"을 기록해두고, 그 직후 일정 시간 안의
// 지도 click은 전부 무시하는 시간창 방식으로 처리한다.
let lastMarkerInteractionAt = 0
const MAP_CLICK_SUPPRESS_WINDOW_MS = 500

function markMarkerInteraction() {
  lastMarkerInteractionAt = Date.now()
}

function ensureInfoOverlayEl() {
  if (infoOverlayEl) return infoOverlayEl
  infoOverlayEl = document.createElement('div')
  infoOverlayEl.className = 'marker-overlay'
  infoOverlayEl.addEventListener('click', markMarkerInteraction)
  return infoOverlayEl
}

function setNameLabelVisible(spotId: string | null, visible: boolean) {
  if (!spotId) return
  const label = nameLabelRegistry.get(spotId)
  if (label) label.setMap(visible ? mapInstance : null)
}

// 사진 + 이름이 있는 hover/pin 카드를 보여준다. 같은 스팟의 "이름만" 라벨과 겹치지 않도록 숨긴다.
function showInfoOverlay(spot: TouristSpot, lat: number, lng: number) {
  if (!mapInstance || !window.kakao?.maps) return
  const el = ensureInfoOverlayEl()
  const image = spot.firstimage
    ? `<img src="${spot.firstimage}" alt="" class="marker-overlay__image" />`
    : '<div class="marker-overlay__image marker-overlay__image--empty">이미지 없음</div>'
  el.innerHTML = `${image}<p class="marker-overlay__title">${escapeHtml(spot.title)}</p>`

  const position = new window.kakao.maps.LatLng(lat, lng)
  if (!infoOverlay) {
    // 카카오 앵커링은 끄고(0,0 = 콘텐츠 좌상단이 핀 위치), 위치 보정은 아래 CSS transform 하나로만 잡는다.
    // 가로 중앙 정렬은 카드 폭(128px)의 절반인 -64px 픽셀값으로 직접 이동시킨다(% 해석 편차 방지).
    infoOverlay = new window.kakao.maps.CustomOverlay({ position, content: el, xAnchor: 0, yAnchor: 0, zIndex: 30 })
  } else {
    infoOverlay.setPosition(position)
  }
  infoOverlay.setMap(mapInstance)

  if (activeSpotId && activeSpotId !== spot.contentid) setNameLabelVisible(activeSpotId, true)
  activeSpotId = spot.contentid
  setNameLabelVisible(activeSpotId, false)
}

function hideInfoOverlay() {
  if (infoOverlay) infoOverlay.setMap(null)
  setNameLabelVisible(activeSpotId, true)
  activeSpotId = null
}

function handleMarkerHover(spot: TouristSpot, lat: number, lng: number) {
  if (isOverlayPinned) return
  showInfoOverlay(spot, lat, lng)
}

function handleMarkerLeave() {
  if (isOverlayPinned) return
  hideInfoOverlay()
}

function handleMarkerClick(spot: TouristSpot, lat: number, lng: number) {
  markMarkerInteraction()
  isOverlayPinned = true
  showInfoOverlay(spot, lat, lng)
  selectSpot(spot)
}

function closePinnedOverlay() {
  if (!isOverlayPinned) return
  isOverlayPinned = false
  hideInfoOverlay()
}

// 클러스터로 묶인(2개 이상) 마커의 이름 라벨은 숨기고, 낱개로 남은 마커만 라벨을 보여준다.
function syncNameLabels(clusters: any[]) {
  const grouped = new Set<string>()
  clusters.forEach((cluster: any) => {
    const members: any[] = cluster.getMarkers?.() ?? []
    if (members.length > 1) members.forEach((m) => grouped.add(m.__spotId))
  })
  nameLabelRegistry.forEach((label, id) => {
    const shouldShow = !grouped.has(id) && id !== activeSpotId
    label.setMap(shouldShow ? mapInstance : null)
  })
}

function initMap() {
  if (mapInstance || !mapContainer.value || !window.kakao?.maps) return
  const center = new window.kakao.maps.LatLng(36.1194, 128.3444)
  mapInstance = new window.kakao.maps.Map(mapContainer.value, { center, level: 8 })
  clusterer = new window.kakao.maps.MarkerClusterer({
    map: mapInstance,
    averageCenter: true,
    minLevel: 5,
    gridSize: 120,
    minClusterSize: 2,
    disableClickZoom: false,
    calculator: [10, 50],
    styles: CLUSTER_STYLES,
  })
  window.kakao.maps.event.addListener(clusterer, 'clustered', (clusters: any[]) => syncNameLabels(clusters))
  window.kakao.maps.event.addListener(mapInstance, 'click', () => {
    if (Date.now() - lastMarkerInteractionAt < MAP_CLICK_SUPPRESS_WINDOW_MS) return
    closePinnedOverlay()
  })
}

function renderMarkers() {
  if (!mapInstance || !clusterer || !window.kakao?.maps) return

  clusterer.clear()
  markerRegistry.clear()
  nameLabelRegistry.forEach((label) => label.setMap(null))
  nameLabelRegistry.clear()

  const markers: any[] = []

  filteredSpots.value.forEach((spot) => {
    const lat = parseFloat(spot.mapy)
    const lng = parseFloat(spot.mapx)
    if (!lat || !lng) return

    const marker = new window.kakao.maps.Marker({
      position: new window.kakao.maps.LatLng(lat, lng),
      image: createMarkerImage(spot.contentid === selectedSpot.value?.contentid),
      title: spot.title,
    })
    ;(marker as any).__spotId = spot.contentid
    window.kakao.maps.event.addListener(marker, 'mouseover', () => handleMarkerHover(spot, lat, lng))
    window.kakao.maps.event.addListener(marker, 'mouseout', () => handleMarkerLeave())
    window.kakao.maps.event.addListener(marker, 'click', () => handleMarkerClick(spot, lat, lng))

    markerRegistry.set(spot.contentid, marker)
    markers.push(marker)

    const labelEl = document.createElement('div')
    labelEl.className = 'marker-name-label'
    labelEl.textContent = spot.title
    const nameLabel = new window.kakao.maps.CustomOverlay({
      position: new window.kakao.maps.LatLng(lat, lng),
      content: labelEl,
      xAnchor: 0.5,
      yAnchor: 0,
      zIndex: 15,
    })
    nameLabel.setMap(mapInstance)
    nameLabelRegistry.set(spot.contentid, nameLabel)
  })

  clusterer.addMarkers(markers)
  clusterer.redraw()

  // 필터/검색으로 목록이 바뀌어 카드가 떠 있던 스팟이 더 이상 안 보이면 카드도 닫는다.
  if (activeSpotId && !markerRegistry.has(activeSpotId)) {
    isOverlayPinned = false
    hideInfoOverlay()
  }
}

function updateActiveMarker() {
  markerRegistry.forEach((marker, contentid) => {
    marker.setImage(createMarkerImage(contentid === selectedSpot.value?.contentid))
  })
}

function selectSpot(spot: TouristSpot) {
  selectedSpot.value = spot
  isSheetExpanded.value = true

  if (mapInstance && window.kakao?.maps) {
    const lat = parseFloat(spot.mapy)
    const lng = parseFloat(spot.mapx)
    if (lat && lng) {
      mapInstance.setLevel(4)
      mapInstance.panTo(new window.kakao.maps.LatLng(lat, lng))
    }
  }
}

function clearSelection() {
  selectedSpot.value = null
  if (mapInstance) mapInstance.setLevel(8)
}

function toggleSheet() {
  isSheetExpanded.value = !isSheetExpanded.value
}

function handleSheetTouchStart(event: TouchEvent) {
  touchStartY = event.touches[0]?.clientY ?? 0
}

function handleSheetTouchEnd(event: TouchEvent) {
  const deltaY = (event.changedTouches[0]?.clientY ?? touchStartY) - touchStartY
  if (deltaY < -30) isSheetExpanded.value = true
  else if (deltaY > 30) isSheetExpanded.value = false
}

watch(selectedSpot, (spot) => {
  updateActiveMarker()
  loadWeather(spot ? extractRegionFromAddress(spot.addr1) : 'Gumi')
})

watch(filteredSpots, () => {
  if (renderMarkersTimer) clearTimeout(renderMarkersTimer)
  renderMarkersTimer = setTimeout(renderMarkers, 150)
})

watch(isKakaoReady, (ready) => {
  if (ready) {
    initMap()
    renderMarkers()
  }
})

onMounted(() => {
  loadSpots()
  loadWeather('Gumi')
  loadKakaoMaps()
    .then(() => {
      isKakaoReady.value = true
    })
    .catch((err) => {
      mapError.value = err instanceof Error ? err.message : '지도를 불러오지 못했습니다.'
    })
})

onUnmounted(() => {
  if (renderMarkersTimer) clearTimeout(renderMarkersTimer)
  if (clusterer) clusterer.clear()
  markerRegistry.clear()
  hideInfoOverlay()
  infoOverlay = null
  infoOverlayEl = null
})
</script>

<template>
  <section class="map-page">
    <div ref="mapContainer" class="map-page__canvas"></div>
    <p v-if="mapError" class="map-page__map-error">{{ mapError }}</p>

    <div class="map-page__top-overlay">
      <label class="map-page__searchbar">
        <Search class="map-page__search-icon" :size="18" />
        <input v-model="keyword" type="text" placeholder="관광지 이름이나 주소로 검색해보세요" />
      </label>
    </div>

    <div v-if="weather" class="map-page__weather" :class="{ 'map-page__weather--dim': isLoadingWeather }">
      <div class="map-page__weather-head">
        <MapPin :size="12" :stroke-width="2.5" />
        <span>{{ weatherRegionLabel }}</span>
      </div>
      <div class="map-page__weather-temp">
        <strong>{{ weather.temp }}°</strong>
        <span class="map-page__weather-desc">{{ weather.weather }}</span>
      </div>
      <div class="map-page__weather-humid">습도 {{ weather.humidity ?? '-' }}%</div>
      <div
        v-if="activityIndex"
        class="map-page__weather-tag"
        :class="`map-page__activity--${activityIndex.level}`"
      >
        {{ activityIndex.text }}
      </div>
    </div>

    <div class="map-page__panel" :class="{ 'map-page__panel--expanded': isSheetExpanded }">
      <div
        class="map-page__panel-handle"
        @click="toggleSheet"
        @touchstart="handleSheetTouchStart"
        @touchend="handleSheetTouchEnd"
      >
        <span class="map-page__panel-grip"></span>
        <p class="map-page__panel-summary">
          {{ selectedSpot ? selectedSpot.title : `주변 관광지 ${filteredSpots.length}곳` }}
        </p>
      </div>

      <div class="map-page__panel-body">
        <template v-if="!selectedSpot">
          <p v-if="isLoadingSpots" class="map-page__status">불러오는 중입니다...</p>
          <p v-else-if="spotsError" class="map-page__status map-page__status--error">{{ spotsError }}</p>
          <p v-else-if="filteredSpots.length === 0" class="map-page__status">검색 결과가 없습니다.</p>

          <template v-else>
            <p class="map-page__panel-count">총 {{ filteredSpots.length }}곳</p>
            <ul class="map-page__spot-list">
              <li v-for="spot in filteredSpots" :key="spot.contentid">
                <button type="button" class="map-page__spot-btn" @click="selectSpot(spot)">
                  <span class="map-page__spot-title">{{ spot.title }}</span>
                  <span class="map-page__spot-addr">{{ spot.addr1 }}</span>
                </button>
              </li>
            </ul>
          </template>
        </template>

        <template v-else>
          <button type="button" class="map-page__back-btn" @click="clearSelection">
            <ChevronLeft :size="16" />
            목록으로
          </button>

          <img
            v-if="selectedSpot.firstimage"
            :src="selectedSpot.firstimage"
            :alt="selectedSpot.title"
            class="map-page__detail-image"
          />
          <div v-else class="map-page__detail-image map-page__detail-image--placeholder">이미지 없음</div>

          <h2 class="map-page__detail-title">{{ selectedSpot.title }}</h2>
          <p class="map-page__detail-addr">{{ selectedSpot.addr1 }}</p>
          <p v-if="selectedSpot.tel" class="map-page__detail-addr">{{ selectedSpot.tel }}</p>

          <div v-if="nearbySpots.length" class="map-page__nearby">
            <p class="map-page__nearby-title">이 근처 관광지</p>
            <ul class="map-page__nearby-list">
              <li v-for="item in nearbySpots" :key="item.spot.contentid">
                <button type="button" class="map-page__nearby-card" @click="selectSpot(item.spot)">
                  <img
                    v-if="item.spot.firstimage"
                    :src="item.spot.firstimage"
                    :alt="item.spot.title"
                    class="map-page__nearby-thumb"
                  />
                  <div v-else class="map-page__nearby-thumb map-page__nearby-thumb--empty">
                    <MapPin :size="16" />
                  </div>
                  <div class="map-page__nearby-info">
                    <span class="map-page__nearby-name">{{ item.spot.title }}</span>
                    <span class="map-page__nearby-addr">{{ item.spot.addr1 }}</span>
                  </div>
                  <span class="map-page__nearby-dist">{{ formatDistance(item.dist) }}</span>
                </button>
              </li>
            </ul>
          </div>
        </template>
      </div>
    </div>
  </section>
</template>

<style scoped>
.map-page {
  position: fixed;
  top: 3.5rem;
  left: 0;
  right: 0;
  bottom: 0;
}

.map-page__canvas {
  width: 100%;
  height: 100%;
  background: var(--color-background-mute);
}

.map-page__map-error {
  position: absolute;
  inset: 0;
  z-index: 3;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-background-mute);
  color: var(--color-text-soft);
  padding: 1rem;
  text-align: center;
}

.map-page__top-overlay {
  position: absolute;
  top: 1rem;
  left: 1rem;
  right: 1rem;
  z-index: 12;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.map-page__searchbar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--color-background);
  border-radius: var(--radius-full);
  box-shadow: var(--shadow-lg);
  padding: 0.75rem 1.1rem;
}

.map-page__searchbar input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  color: var(--color-text);
  font-size: var(--text-md);
}

.map-page__search-icon {
  flex-shrink: 0;
  color: var(--color-text-soft);
}

/* 지도 우측 상단 날씨 배지 */
.map-page__weather {
  position: absolute;
  top: 1rem;
  right: 1rem;
  z-index: 11;
  width: 148px;
  padding: 0.7rem 0.85rem;
  background: var(--color-background);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  transition: opacity 0.2s ease;
}

.map-page__weather--dim {
  opacity: 0.55;
}

.map-page__weather-head {
  display: flex;
  align-items: center;
  gap: 0.2rem;
  color: var(--color-primary);
  font-size: var(--text-xs);
  font-weight: var(--weight-bold);
}

.map-page__weather-temp {
  display: flex;
  align-items: baseline;
  gap: 0.35rem;
  margin-top: 0.15rem;
}

.map-page__weather-temp strong {
  font-size: var(--text-xl);
  font-weight: var(--weight-extrabold);
  color: var(--color-heading);
}

.map-page__weather-desc {
  font-size: var(--text-xs);
  color: var(--color-text-soft);
}

.map-page__weather-humid {
  font-size: var(--text-xs);
  color: var(--color-text-soft);
  margin-top: 0.1rem;
}

.map-page__weather-tag {
  margin-top: 0.5rem;
  border-radius: var(--radius-sm);
  padding: 0.3rem 0.4rem;
  font-size: var(--text-xs);
  font-weight: var(--weight-bold);
  line-height: 1.3;
  text-align: center;
}

.map-page__panel {
  position: absolute;
  top: 4.75rem;
  left: 1rem;
  bottom: 1rem;
  width: 360px;
  max-width: calc(100% - 2rem);
  background: var(--color-background);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  z-index: 10;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.map-page__panel-handle {
  display: none;
}

.map-page__panel-body {
  flex: 1;
  overflow-y: auto;
  padding: 0 1.1rem 1.1rem;
}

.map-page__panel-count {
  color: var(--color-text-soft);
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  padding: 1rem 0 0.5rem;
}

.map-page__status {
  padding: 2rem 0;
  text-align: center;
  color: var(--color-text-soft);
  font-size: var(--text-sm);
}

.map-page__status--error {
  color: var(--color-danger);
}

.map-page__spot-list {
  list-style: none;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.map-page__spot-btn {
  width: 100%;
  text-align: left;
  padding: 0.75rem 0.9rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-background);
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.map-page__spot-btn:hover {
  border-color: var(--color-primary);
  background: var(--color-primary-soft);
}

.map-page__spot-title {
  font-weight: var(--weight-bold);
  font-size: var(--text-md);
}

.map-page__spot-addr {
  color: var(--color-text-soft);
  font-size: var(--text-xs);
}

.map-page__back-btn {
  display: flex;
  align-items: center;
  gap: 0.2rem;
  border: none;
  background: transparent;
  color: var(--color-text-soft);
  font-weight: var(--weight-semibold);
  font-size: var(--text-sm);
  padding: 1rem 0 0.5rem;
}

.map-page__detail-image {
  width: 100%;
  height: 160px;
  object-fit: cover;
  border-radius: var(--radius-md);
  background: var(--color-background-mute);
  margin-bottom: 0.75rem;
}

.map-page__detail-image--placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-soft);
  font-size: var(--text-sm);
}

.map-page__detail-title {
  font-size: var(--text-lg);
  margin-bottom: 0.3rem;
}

.map-page__detail-addr {
  color: var(--color-text-soft);
  font-size: var(--text-sm);
  margin-bottom: 0.25rem;
}

.map-page__nearby {
  margin-top: 1.25rem;
}

.map-page__nearby-title {
  font-size: var(--text-md);
  font-weight: var(--weight-extrabold);
  color: var(--color-heading);
  margin-bottom: 0.6rem;
}

.map-page__nearby-list {
  list-style: none;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.map-page__nearby-card {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-background);
  text-align: left;
  transition:
    border-color 0.15s ease,
    background 0.15s ease;
}

.map-page__nearby-card:hover {
  border-color: var(--color-primary);
  background: var(--color-primary-soft);
}

.map-page__nearby-thumb {
  flex-shrink: 0;
  width: 46px;
  height: 46px;
  border-radius: var(--radius-sm);
  object-fit: cover;
  background: var(--color-background-mute);
}

.map-page__nearby-thumb--empty {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-soft);
}

.map-page__nearby-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.map-page__nearby-name {
  font-size: var(--text-sm);
  font-weight: var(--weight-bold);
  color: var(--color-heading);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.map-page__nearby-addr {
  font-size: var(--text-xs);
  color: var(--color-text-soft);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.map-page__nearby-dist {
  flex-shrink: 0;
  font-size: var(--text-xs);
  font-weight: var(--weight-bold);
  color: var(--color-primary);
  background: var(--color-primary-soft);
  padding: 0.2rem 0.5rem;
  border-radius: var(--radius-full);
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
    bottom: calc(3.5rem + env(safe-area-inset-bottom, 0px));
  }

  .map-page__top-overlay {
    right: 1rem;
  }

  /* 모바일은 검색바가 전체폭이라 날씨 배지를 그 아래로 내린다. */
  .map-page__weather {
    top: 4.4rem;
    right: 0.8rem;
    width: 132px;
  }

  .map-page__panel {
    top: auto;
    left: 0;
    right: 0;
    bottom: 0;
    width: 100%;
    max-width: none;
    height: 75vh;
    max-height: 75vh;
    border-radius: var(--radius-lg) var(--radius-lg) 0 0;
    transform: translateY(calc(100% - 6.5rem));
    transition: transform 0.32s cubic-bezier(0.32, 0.72, 0, 1);
  }

  .map-page__panel--expanded {
    transform: translateY(0);
  }

  .map-page__panel-handle {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.4rem;
    padding: 0.75rem 1rem 0.5rem;
    cursor: pointer;
  }

  .map-page__panel-grip {
    width: 36px;
    height: 4px;
    border-radius: var(--radius-full);
    background: var(--color-border-hover);
  }

  .map-page__panel-summary {
    font-weight: var(--weight-bold);
    font-size: var(--text-md);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 100%;
  }
}

@media (min-width: 721px) {
  .map-page__top-overlay {
    width: 360px;
  }
}
</style>

<style>
/* 핀 아래 항상 떠 있는 이름 라벨 — 흰색 라운드 알약 형태 */
.marker-name-label {
  margin-top: 5px;
  max-width: 132px;
  padding: 3px 9px;
  background: #ffffff;
  border: 1px solid rgba(33, 37, 41, 0.06);
  border-radius: 999px;
  box-shadow: 0 2px 8px rgba(33, 37, 41, 0.18);
  color: #212529;
  font-size: 11px;
  font-weight: 700;
  line-height: 1.4;
  letter-spacing: -0.01em;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  pointer-events: none;
}

.marker-overlay {
  position: relative;
  display: flex;
  flex-direction: column;
  width: 135px;
  /* 가로: 폭의 절반(-64px)만큼 왼쪽으로 옮겨 핀 정중앙 정렬. 세로: 핀(최대 36px)을 넘어서도록 위로 올림. */
  transform: translate(-67px, calc(-100% - 42px));
  background: #ffffff;
  border-radius: var(--radius-md, 12px);
  padding: 0.4rem;
  box-shadow: 0 8px 20px rgba(33, 37, 41, 0.2);
  cursor: pointer;
}

.marker-overlay::after {
  content: '';
  position: absolute;
  left: 50%;
  bottom: -5px;
  width: 10px;
  height: 10px;
  background: #ffffff;
  transform: translateX(-50%) rotate(45deg);
  border-radius: 2px;
  z-index: -1;
}

.marker-overlay__image {
  width: 120px;
  height: 80px;
  border-radius: var(--radius-sm, 8px);
  object-fit: cover;
  background: var(--color-background-mute, #f1f3f5);
  margin-bottom: 0.35rem;
}

.marker-overlay__image--empty {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-soft, #868e96);
  font-size: var(--text-xs);
}

.marker-overlay__title {
  display: block;
  color: var(--color-heading, #212529);
  font-size: var(--text-xs);
  font-weight: var(--weight-bold);
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
