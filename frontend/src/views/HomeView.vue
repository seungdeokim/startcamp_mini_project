<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { getPosts } from '@/api/posts'
import { ApiError } from '@/api/client'
import type { Post } from '@/types/post'

const RECENT_COUNT = 5

const recentPosts = ref<Post[]>([])
const isLoading = ref(true)
const errorMessage = ref('')

onMounted(async () => {
  try {
    const posts = await getPosts()
    recentPosts.value = [...posts].sort((a, b) => b.id - a.id).slice(0, RECENT_COUNT)
  } catch (err) {
    errorMessage.value = err instanceof ApiError ? err.message : '게시글을 불러오지 못했습니다.'
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <section class="home">
    <div class="home__banner">
      <h1>지역 정보 공유 커뮤니티 LocalHub</h1>
      <p>선정 권역(구미/경북) 지역 정보를 한눈에 만나보세요</p>
    </div>

    <nav class="home__shortcuts">
      <RouterLink to="/board" class="home__shortcut-card">게시판</RouterLink>
      <RouterLink to="/info" class="home__shortcut-card">지역정보</RouterLink>
      <RouterLink to="/map" class="home__shortcut-card">지도</RouterLink>
    </nav>

    <div class="home__recent">
      <h2>최근 게시글</h2>
      <p v-if="isLoading" class="home__placeholder">불러오는 중입니다...</p>
      <p v-else-if="errorMessage" class="home__placeholder">{{ errorMessage }}</p>
      <p v-else-if="recentPosts.length === 0" class="home__placeholder">등록된 게시글이 없습니다.</p>
      <ul v-else class="home__recent-list">
        <li v-for="post in recentPosts" :key="post.id">
          <RouterLink :to="`/board/${post.id}`">{{ post.title }}</RouterLink>
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
  background: var(--color-primary-soft);
  border-radius: 12px;
  padding: 2rem 1.5rem;
  text-align: center;
}

.home__banner h1 {
  color: var(--color-primary);
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}

.home__shortcuts {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.home__shortcut-card {
  border: 1px solid var(--color-border);
  border-radius: 10px;
  padding: 1.25rem 1rem;
  text-align: center;
  font-weight: 600;
}

.home__shortcut-card:hover {
  border-color: var(--color-primary);
  text-decoration: none;
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
}

.home__recent-list li {
  padding: 0.6rem 0;
  border-bottom: 1px solid var(--color-border);
}

.home__recent-list a {
  color: var(--color-text);
}

.home__recent-list a:hover {
  color: var(--color-primary);
}

@media (max-width: 640px) {
  .home__shortcuts {
    grid-template-columns: 1fr;
  }
}
</style>
