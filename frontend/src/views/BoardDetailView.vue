<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getPost, deletePost } from '@/api/posts'
import { ApiError } from '@/api/client'
import { usePostAuth } from '@/composables/usePostAuth'
import type { Post } from '@/types/post'
import PasswordModal from '@/components/board/PasswordModal.vue'

const props = defineProps<{ id: string }>()
const router = useRouter()
const { pendingPassword } = usePostAuth()

const post = ref<Post | null>(null)
const isLoading = ref(true)
const errorMessage = ref('')

const modalMode = ref<'edit' | 'delete' | null>(null)
const modalError = ref('')
const isSubmitting = ref(false)

async function loadPost() {
  isLoading.value = true
  errorMessage.value = ''
  try {
    post.value = await getPost(Number(props.id))
  } catch (err) {
    errorMessage.value = err instanceof ApiError ? err.message : '게시글을 불러오지 못했습니다.'
  } finally {
    isLoading.value = false
  }
}

onMounted(loadPost)

function openModal(mode: 'edit' | 'delete') {
  modalMode.value = mode
  modalError.value = ''
}

function closeModal() {
  modalMode.value = null
  modalError.value = ''
}

async function handleConfirm(password: string) {
  if (!modalMode.value) return
  isSubmitting.value = true
  modalError.value = ''

  try {
    if (modalMode.value === 'delete') {
      await deletePost(Number(props.id), password)
      router.push('/board')
      return
    }

    // 수정: 상세에서는 비밀번호를 임시로만 들고 수정 화면으로 이동하고,
    // 실제 검증은 수정 화면에서 저장할 때 PUT 요청으로 이루어진다.
    pendingPassword.value = password
    router.push(`/board/${props.id}/edit`)
  } catch (err) {
    modalError.value =
      err instanceof ApiError && err.status === 403 ? '비밀번호가 일치하지 않습니다.' : '요청 처리 중 오류가 발생했습니다.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <section class="board-detail">
    <p v-if="isLoading" class="board-detail__status">불러오는 중입니다...</p>
    <p v-else-if="errorMessage" class="board-detail__status board-detail__status--error">{{ errorMessage }}</p>

    <template v-else-if="post">
      <div class="board-detail__card">
        <h1 class="board-detail__title">{{ post.title }}</h1>
        <p class="board-detail__author">작성자: {{ post.author }}</p>
        <div class="board-detail__content">{{ post.content }}</div>

        <div class="board-detail__actions">
          <button type="button" class="board-detail__edit-btn" @click="openModal('edit')">수정</button>
          <button type="button" class="board-detail__delete-btn" @click="openModal('delete')">삭제</button>
        </div>
      </div>
    </template>

    <PasswordModal
      :visible="modalMode !== null"
      :error-message="modalError"
      :is-submitting="isSubmitting"
      @confirm="handleConfirm"
      @cancel="closeModal"
    />
  </section>
</template>

<style scoped>
.board-detail__status {
  padding: 2rem 0;
  text-align: center;
  color: var(--color-text-soft);
}

.board-detail__status--error {
  color: var(--color-danger);
}

.board-detail__card {
  background: var(--color-background);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  padding: 1.5rem;
}

.board-detail__title {
  font-size: var(--text-xl);
  font-weight: var(--weight-extrabold);
  margin-bottom: 0.4rem;
}

.board-detail__author {
  color: var(--color-text-soft);
  font-size: var(--text-sm);
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--color-border);
  margin-bottom: 1.25rem;
}

.board-detail__content {
  min-height: 8rem;
  white-space: pre-wrap;
  line-height: 1.7;
}

.board-detail__actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 2rem;
}

.board-detail__edit-btn,
.board-detail__delete-btn {
  padding: 0.55rem 1.2rem;
  border-radius: var(--radius-full);
  border: 1px solid var(--color-border);
  background: var(--color-background);
  font-weight: 600;
}

.board-detail__edit-btn:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.board-detail__delete-btn {
  color: var(--color-danger);
  border-color: var(--color-danger-soft);
}

.board-detail__delete-btn:hover {
  background: var(--color-danger-soft);
}
</style>
