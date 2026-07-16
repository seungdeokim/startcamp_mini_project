<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { getPosts } from '@/api/posts'
import { ApiError } from '@/api/client'
import type { Post } from '@/types/post'
import Pagination from '@/components/common/Pagination.vue'
import SearchBar from '@/components/common/SearchBar.vue'

const PAGE_SIZE = 10

const router = useRouter()

const posts = ref<Post[]>([])
const isLoading = ref(true)
const errorMessage = ref('')
const keyword = ref('')
const currentPage = ref(1)

async function loadPosts() {
  isLoading.value = true
  errorMessage.value = ''
  try {
    posts.value = await getPosts()
  } catch (err) {
    errorMessage.value = err instanceof ApiError ? err.message : '게시글을 불러오지 못했습니다.'
  } finally {
    isLoading.value = false
  }
}

onMounted(loadPosts)

const filteredPosts = computed(() => {
  const sorted = [...posts.value].sort((a, b) => b.id - a.id)
  const keywordTrimmed = keyword.value.trim().toLowerCase()
  if (!keywordTrimmed) return sorted
  return sorted.filter((post) => post.title.toLowerCase().includes(keywordTrimmed))
})

const totalPages = computed(() => Math.max(1, Math.ceil(filteredPosts.value.length / PAGE_SIZE)))

const pagedPosts = computed(() => {
  const start = (currentPage.value - 1) * PAGE_SIZE
  return filteredPosts.value.slice(start, start + PAGE_SIZE)
})

// 검색어가 바뀌면 첫 페이지로 되돌린다.
watch(keyword, () => {
  currentPage.value = 1
})

function handlePageChange(page: number) {
  currentPage.value = page
}

function goToDetail(id: number) {
  router.push(`/board/${id}`)
}
</script>

<template>
  <section class="board-list">
    <h1>게시판</h1>

    <div class="board-list__toolbar">
      <SearchBar v-model="keyword" placeholder="게시글 검색어를 입력하세요" class="board-list__search" />
      <RouterLink to="/board/write" class="board-list__write-btn">+ 글쓰기</RouterLink>
    </div>

    <p v-if="isLoading" class="board-list__status">불러오는 중입니다...</p>
    <p v-else-if="errorMessage" class="board-list__status board-list__status--error">{{ errorMessage }}</p>
    <p v-else-if="pagedPosts.length === 0" class="board-list__status">게시글이 없습니다.</p>

    <ul v-else class="board-list__list">
      <li v-for="post in pagedPosts" :key="post.id">
        <button type="button" class="board-list__row" @click="goToDetail(post.id)">
          <span class="board-list__id">{{ post.id }}</span>
          <span class="board-list__title">{{ post.title }}</span>
          <span class="board-list__author">{{ post.author }}</span>
        </button>
      </li>
    </ul>

    <Pagination :current-page="currentPage" :total-pages="totalPages" @change="handlePageChange" />
  </section>
</template>

<style scoped>
.board-list__toolbar {
  display: flex;
  gap: 0.5rem;
  margin: 1rem 0 1.25rem;
}

.board-list__search {
  flex: 1;
  min-width: 0;
}

.board-list__write-btn {
  display: inline-flex;
  align-items: center;
  padding: 0 1.3rem;
  border-radius: var(--radius-full);
  background: var(--color-primary);
  color: #fff;
  font-size: var(--text-sm);
  font-weight: var(--weight-bold);
  white-space: nowrap;
  box-shadow: var(--shadow-sm);
}

.board-list__write-btn:hover {
  text-decoration: none;
  background: var(--color-primary-hover);
}

.board-list__status {
  padding: 2rem 0;
  text-align: center;
  color: var(--color-text-soft);
  font-size: var(--text-sm);
}

.board-list__status--error {
  color: var(--color-danger);
}

.board-list__list {
  list-style: none;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.board-list__row {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.9rem;
  padding: 0.9rem 1rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-background);
  box-shadow: var(--shadow-sm);
  color: var(--color-text);
  text-align: left;
  cursor: pointer;
}

.board-list__row:hover,
.board-list__row:focus-visible {
  background: var(--color-primary-soft);
  outline: none;
}

.board-list__id {
  flex-shrink: 0;
  width: 2rem;
  color: var(--color-text-soft);
  font-size: var(--text-xs);
}

.board-list__title {
  flex: 1;
  font-size: var(--text-md);
  font-weight: var(--weight-semibold);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.board-list__author {
  flex-shrink: 0;
  color: var(--color-text-soft);
  font-size: var(--text-xs);
}

@media (max-width: 480px) {
  .board-list__toolbar {
    flex-wrap: wrap;
  }

  .board-list__search {
    flex-basis: 100%;
  }
}
</style>
