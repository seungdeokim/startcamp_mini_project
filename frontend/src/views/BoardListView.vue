<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { getPosts } from '@/api/posts'
import { ApiError } from '@/api/client'
import type { Post } from '@/types/post'
import Pagination from '@/components/common/Pagination.vue'

const PAGE_SIZE = 10

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

function handleSearch() {
  currentPage.value = 1
}

function handlePageChange(page: number) {
  currentPage.value = page
}
</script>

<template>
  <section class="board-list">
    <h1>게시판</h1>

    <div class="board-list__toolbar">
      <input
        v-model="keyword"
        type="text"
        placeholder="게시글 검색어를 입력하세요"
        class="board-list__search"
        @keyup.enter="handleSearch"
      />
      <button type="button" class="board-list__search-btn" @click="handleSearch">검색</button>
      <RouterLink to="/board/write" class="board-list__write-btn">+ 글쓰기</RouterLink>
    </div>

    <p v-if="isLoading" class="board-list__status">불러오는 중입니다...</p>
    <p v-else-if="errorMessage" class="board-list__status board-list__status--error">{{ errorMessage }}</p>
    <p v-else-if="pagedPosts.length === 0" class="board-list__status">게시글이 없습니다.</p>

    <div v-else class="board-list__table-wrap">
      <table class="board-list__table">
        <thead>
          <tr>
            <th>번호</th>
            <th>제목</th>
            <th>작성자</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="post in pagedPosts" :key="post.id">
            <td>{{ post.id }}</td>
            <td class="board-list__title-cell">
              <RouterLink :to="`/board/${post.id}`">{{ post.title }}</RouterLink>
            </td>
            <td>{{ post.author }}</td>
          </tr>
        </tbody>
      </table>
    </div>

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
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: var(--color-background);
  color: var(--color-text);
}

.board-list__search-btn {
  padding: 0.5rem 1rem;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: var(--color-background-soft);
}

.board-list__write-btn {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  background: var(--color-primary);
  color: #fff;
  font-weight: 600;
  white-space: nowrap;
}

.board-list__write-btn:hover {
  text-decoration: none;
  opacity: 0.9;
}

.board-list__status {
  padding: 2rem 0;
  text-align: center;
  color: var(--color-text-soft);
}

.board-list__status--error {
  color: var(--color-danger);
}

.board-list__table-wrap {
  overflow-x: auto;
}

.board-list__table {
  width: 100%;
  min-width: 420px;
  border-collapse: collapse;
}

.board-list__table th,
.board-list__table td {
  padding: 0.75rem 0.5rem;
  border-bottom: 1px solid var(--color-border);
  text-align: left;
}

.board-list__table th {
  color: var(--color-text-soft);
  font-weight: 600;
  font-size: 0.85rem;
}

.board-list__title-cell a {
  color: var(--color-text);
}

@media (max-width: 480px) {
  .board-list__toolbar {
    flex-wrap: wrap;
  }

  .board-list__search {
    flex-basis: 100%;
  }
}

.board-list__title-cell a:hover {
  color: var(--color-primary);
}
</style>
