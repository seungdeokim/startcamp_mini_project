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
    <div class="home__banner">
      <h1>지역 정보 공유 커뮤니티 Gumi Log</h1>
      <p>구미/경북 지역 정보를 한눈에 만나보세요!</p>
    </div>

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

    <div class="home__recent">
      <h2>최근 게시글</h2>
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
    </div>
  </section>
</template>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.home__banner {
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 2.25rem 1.5rem;
  text-align: center;
}

.home__banner h1 {
  color: var(--color-heading);
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
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
  font-size: 0.8rem;
  margin-bottom: 0.15rem;
}

.home__weather-main {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
}

.home__weather-main strong {
  font-size: 1.5rem;
}

.home__weather-main span {
  color: var(--color-text-soft);
  font-size: 0.9rem;
}

.home__weather-side {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.4rem;
}

.home__weather-humidity {
  color: var(--color-text-soft);
  font-size: 0.8rem;
}

.home__weather-activity {
  border-radius: var(--radius-full);
  padding: 0.3rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 700;
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
  font-weight: 700;
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

.home__recent h2 {
  font-size: 1.1rem;
  margin-bottom: 0.75rem;
}

.home__placeholder {
  color: var(--color-text-soft);
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
  gap: 0.75rem;
  padding: 0.9rem 1rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-background);
  box-shadow: var(--shadow-sm);
  color: var(--color-text);
  font-weight: 500;
  text-decoration: none;
}

.home__recent-list a:hover {
  background: var(--color-primary-soft);
  text-decoration: none;
}

@media (max-width: 640px) {
  .home__shortcuts {
    grid-template-columns: 1fr;
  }
}
</style>
