<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { getPosts } from '@/api/posts'
import { getWeather } from '@/api/weather'
import { ApiError } from '@/api/client'
import { calculateActivityIndex } from '@/utils/activityIndex'
import type { Post } from '@/types/post'
import type { WeatherInfo } from '@/types/weather'
import { NotebookText, MapPin, Map } from '@lucide/vue'

const RECENT_COUNT = 5
const WEATHER_REGIONS = [
  { key: 'Gumi', label: '구미' },
  { key: 'Daegu', label: '대구' },
] as const

interface RegionWeather {
  key: string
  label: string
  data: WeatherInfo | null
  isLoading: boolean
  error: string
}

const recentPosts = ref<Post[]>([])
const isLoading = ref(true)
const errorMessage = ref('')

const weatherList = ref<RegionWeather[]>(
  WEATHER_REGIONS.map((region) => ({
    key: region.key,
    label: region.label,
    data: null,
    isLoading: true,
    error: '',
  })),
)

function activityFor(data: WeatherInfo | null) {
  if (!data || data.humidity === undefined) return null
  return calculateActivityIndex(data.temp, data.humidity, data.weather)
}

async function loadRegionWeather(entry: RegionWeather) {
  entry.isLoading = true
  entry.error = ''
  try {
    entry.data = await getWeather(entry.key)
  } catch (err) {
    entry.error = err instanceof ApiError ? err.message : '날씨 정보를 불러오지 못했습니다.'
  } finally {
    entry.isLoading = false
  }
}

onMounted(async () => {
  try {
    const posts = await getPosts()
    recentPosts.value = [...posts].sort((a, b) => b.id - a.id).slice(0, RECENT_COUNT)
  } catch (err) {
    errorMessage.value = err instanceof ApiError ? err.message : '게시글을 불러오지 못했습니다.'
  } finally {
    isLoading.value = false
  }

  weatherList.value.forEach(loadRegionWeather)
})
</script>

<template>
  <section class="home">
    <header class="home__hero">
      <div class="home__hero-content">
        <span class="home__hero-badge">
          <MapPin :size="13" :stroke-width="2.5" />
          구미 · 경북 로컬 커뮤니티
        </span>
        <h1 class="home__hero-title">
          우리 동네 이야기,<br />
          <em>Gumi Log</em>에서 만나요
        </h1>
        <p class="home__hero-subtitle">실시간 날씨부터 관광지, 이웃 소식까지 한눈에</p>
        <div class="home__hero-actions">
          <RouterLink to="/info" class="home__hero-btn home__hero-btn--primary">
            <MapPin :size="16" :stroke-width="2.5" />
            관광지 둘러보기
          </RouterLink>
          <RouterLink to="/map" class="home__hero-btn">
            <Map :size="16" :stroke-width="2.5" />
            지도에서 보기
          </RouterLink>
        </div>
      </div>
      <span class="home__hero-glow" aria-hidden="true"></span>
      <span class="home__hero-glow home__hero-glow--sm" aria-hidden="true"></span>
    </header>

    <section class="home__section">
      <p class="home__section-title">오늘의 날씨</p>
      <div class="home__weather-grid">
        <div v-for="entry in weatherList" :key="entry.key" class="home__weather">
          <p v-if="entry.isLoading" class="home__placeholder">날씨 정보를 불러오는 중...</p>
          <p v-else-if="entry.error" class="home__placeholder">{{ entry.error }}</p>

          <template v-else-if="entry.data">
            <div class="home__weather-info">
              <p class="home__weather-region">{{ entry.label }} 현재 날씨</p>
              <p class="home__weather-main">
                <strong>{{ entry.data.temp }}°C</strong>
                <span>{{ entry.data.weather }}</span>
              </p>
            </div>
            <div class="home__weather-side">
              <span class="home__weather-humidity">습도 {{ entry.data.humidity ?? '-' }}%</span>
              <span
                v-if="activityFor(entry.data)"
                class="home__weather-activity"
                :class="`home__weather-activity--${activityFor(entry.data)!.level}`"
              >
                {{ activityFor(entry.data)!.text }}
              </span>
            </div>
          </template>
        </div>
      </div>
    </section>

    <section class="home__section">
      <p class="home__section-title">바로가기</p>
      <nav class="home__shortcuts">
        <RouterLink to="/board" class="home__shortcut-card">
          <NotebookText class="home__shortcut-icon" :size="22" />
          게시판
        </RouterLink>
        <RouterLink to="/info" class="home__shortcut-card">
          <MapPin class="home__shortcut-icon" :size="22" />
          지역정보
        </RouterLink>
        <RouterLink to="/map" class="home__shortcut-card">
          <Map class="home__shortcut-icon" :size="22" />
          지도
        </RouterLink>
      </nav>
    </section>

    <section class="home__section">
      <div class="home__section-head">
        <p class="home__section-title">최근 게시글</p>
        <RouterLink to="/board" class="home__section-more">전체보기</RouterLink>
      </div>
      <p v-if="isLoading" class="home__placeholder">불러오는 중입니다...</p>
      <p v-else-if="errorMessage" class="home__placeholder">{{ errorMessage }}</p>
      <p v-else-if="recentPosts.length === 0" class="home__placeholder">등록된 게시글이 없습니다.</p>
      <ul v-else class="home__recent-list">
        <li v-for="post in recentPosts" :key="post.id">
          <RouterLink :to="`/board/${post.id}`">
            <span class="home__recent-title">{{ post.title }}</span>
            <span class="home__recent-author">{{ post.author }}</span>
          </RouterLink>
        </li>
      </ul>
    </section>
  </section>
</template>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  gap: 1.75rem;
}

.home__hero {
  position: relative;
  overflow: hidden;
  background: var(--gradient-brand);
  border-radius: var(--radius-xl);
  padding: 2.5rem 1.75rem;
  box-shadow: 0 14px 34px rgba(242, 106, 31, 0.28);
  isolation: isolate;
}

.home__hero-content {
  position: relative;
  z-index: 2;
}

.home__hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  background: rgba(255, 255, 255, 0.22);
  color: #fff;
  font-size: var(--text-xs);
  font-weight: var(--weight-bold);
  padding: 0.35rem 0.75rem;
  border-radius: var(--radius-full);
  backdrop-filter: blur(4px);
  margin-bottom: 1rem;
}

.home__hero-title {
  color: #fff;
  font-size: var(--text-2xl);
  font-weight: var(--weight-extrabold);
  line-height: 1.32;
  letter-spacing: -0.03em;
  margin-bottom: 0.6rem;
  text-shadow: 0 2px 8px rgba(180, 70, 15, 0.25);
}

.home__hero-title em {
  font-style: normal;
  color: #fff;
  background: rgba(255, 255, 255, 0.2);
  padding: 0 0.35rem;
  border-radius: var(--radius-sm);
}

.home__hero-subtitle {
  color: rgba(255, 255, 255, 0.92);
  font-size: var(--text-md);
  font-weight: var(--weight-medium);
  margin-bottom: 1.4rem;
}

.home__hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
}

.home__hero-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.6rem 1.1rem;
  border-radius: var(--radius-full);
  font-size: var(--text-sm);
  font-weight: var(--weight-bold);
  color: #fff;
  background: rgba(255, 255, 255, 0.18);
  border: 1px solid rgba(255, 255, 255, 0.35);
  text-decoration: none;
  transition:
    transform 0.15s ease,
    background 0.15s ease;
}

.home__hero-btn:hover {
  transform: translateY(-2px);
  text-decoration: none;
  background: rgba(255, 255, 255, 0.28);
}

.home__hero-btn--primary {
  color: var(--color-primary-hover);
  background: #fff;
  border-color: #fff;
}

.home__hero-btn--primary:hover {
  background: #fff;
}

.home__hero-glow {
  position: absolute;
  z-index: 1;
  width: 220px;
  height: 220px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.22);
  top: -80px;
  right: -50px;
  filter: blur(8px);
}

.home__hero-glow--sm {
  width: 120px;
  height: 120px;
  top: auto;
  bottom: -55px;
  right: 32%;
  background: rgba(255, 255, 255, 0.16);
}

.home__section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.home__section-title {
  font-size: var(--text-md);
  font-weight: var(--weight-extrabold);
  color: var(--color-heading);
  letter-spacing: -0.02em;
}

.home__section-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
}

.home__section-more {
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  color: var(--color-text-soft);
  text-decoration: none;
}

.home__section-more:hover {
  color: var(--color-primary);
  text-decoration: none;
}

.home__weather-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.home__weather {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 1.1rem 1.4rem;
  box-shadow: var(--shadow-sm);
}

.home__weather-region {
  color: var(--color-text-soft);
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  margin-bottom: 0.15rem;
}

.home__weather-main {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
}

.home__weather-main strong {
  font-size: var(--text-xl);
  font-weight: var(--weight-extrabold);
}

.home__weather-main span {
  color: var(--color-text-soft);
  font-size: var(--text-sm);
}

.home__weather-side {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.4rem;
}

.home__weather-humidity {
  color: var(--color-text-soft);
  font-size: var(--text-xs);
}

.home__weather-activity {
  border-radius: var(--radius-full);
  padding: 0.3rem 0.75rem;
  font-size: var(--text-xs);
  font-weight: var(--weight-bold);
  white-space: nowrap;
}

.home__weather-activity--danger {
  color: var(--color-danger);
  background: var(--color-danger-soft);
}

.home__weather-activity--warning {
  color: var(--color-warning);
  background: var(--color-warning-soft);
}

.home__weather-activity--info {
  color: var(--color-info);
  background: var(--color-info-soft);
}

.home__weather-activity--success {
  color: var(--color-success);
  background: var(--color-success-soft);
}

@media (max-width: 480px) {
  .home__weather-grid {
    grid-template-columns: 1fr;
  }

  .home__weather {
    flex-direction: column;
    align-items: flex-start;
  }

  .home__weather-side {
    align-items: flex-start;
    flex-direction: row;
  }
}

.home__shortcuts {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.home__shortcut-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.4rem;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 1.4rem 1rem;
  text-align: center;
  font-size: var(--text-sm);
  font-weight: var(--weight-bold);
  color: var(--color-text);
  box-shadow: var(--shadow-sm);
  transition:
    transform 0.15s ease,
    border-color 0.15s ease;
}

.home__shortcut-icon {
  color: var(--color-text-soft);
}

.home__shortcut-card:hover {
  border-color: var(--color-primary);
  text-decoration: none;
  transform: translateY(-2px);
}

.home__placeholder {
  color: var(--color-text-soft);
  font-size: var(--text-sm);
}

.home__recent-list {
  list-style: none;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.home__recent-list a {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.9rem 1rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-background);
  box-shadow: var(--shadow-sm);
  color: var(--color-text);
  text-decoration: none;
  transition:
    border-color 0.15s ease,
    background 0.15s ease;
}

.home__recent-list a:hover {
  border-color: var(--color-primary);
  background: var(--color-primary-soft);
  text-decoration: none;
}

.home__recent-title {
  flex: 1;
  min-width: 0;
  font-size: var(--text-sm);
  font-weight: var(--weight-semibold);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.home__recent-author {
  flex-shrink: 0;
  font-size: var(--text-xs);
  color: var(--color-text-soft);
}

@media (max-width: 640px) {
  .home__shortcuts {
    grid-template-columns: 1fr;
  }
}
</style>
