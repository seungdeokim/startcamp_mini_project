<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getPost, createPost, updatePost } from '@/api/posts'
import { ApiError } from '@/api/client'
import { usePostAuth } from '@/composables/usePostAuth'

const props = defineProps<{ id?: string }>()
const router = useRouter()
const { pendingPassword } = usePostAuth()

const isEditMode = computed(() => Boolean(props.id))

const title = ref('')
const author = ref('')
const content = ref('')
const password = ref('')
const isLoading = ref(false)
const isSubmitting = ref(false)
const errorMessage = ref('')

onMounted(async () => {
  if (!isEditMode.value) return

  password.value = pendingPassword.value

  isLoading.value = true
  try {
    const post = await getPost(Number(props.id))
    title.value = post.title
    content.value = post.content
  } catch {
    errorMessage.value = '게시글을 불러오지 못했습니다.'
  } finally {
    isLoading.value = false
  }
})

onUnmounted(() => {
  pendingPassword.value = ''
})

async function handleSubmit() {
  if (!title.value.trim() || !content.value.trim() || !password.value) {
    errorMessage.value = '제목, 내용, 비밀번호를 모두 입력해주세요.'
    return
  }

  isSubmitting.value = true
  errorMessage.value = ''

  try {
    if (isEditMode.value) {
      await updatePost(Number(props.id), title.value, content.value, password.value)
      router.push(`/board/${props.id}`)
    } else {
      const result = await createPost({
        title: title.value,
        content: content.value,
        password: password.value,
        ...(author.value.trim() ? { author: author.value.trim() } : {}),
      })
      router.push(`/board/${result.post_id}`)
    }
  } catch (err) {
    errorMessage.value =
      err instanceof ApiError && err.status === 403
        ? '비밀번호가 일치하지 않습니다.'
        : '저장 중 오류가 발생했습니다.'
  } finally {
    isSubmitting.value = false
  }
}

function handleCancel() {
  router.back()
}
</script>

<template>
  <section class="board-write">
    <h1>{{ isEditMode ? '게시글 수정' : '게시글 작성' }}</h1>

    <p v-if="isLoading" class="board-write__status">불러오는 중입니다...</p>

    <form v-else class="board-write__form board-write__card" @submit.prevent="handleSubmit">
      <label class="board-write__field">
        <span>제목</span>
        <input v-model="title" type="text" placeholder="제목을 입력하세요" />
      </label>

      <label v-if="!isEditMode" class="board-write__field">
        <span>닉네임</span>
        <input v-model="author" type="text" placeholder="ㅇㅇ" maxlength="20" />
        <small>※ 입력하지 않으면 'ㅇㅇ'로 표시됩니다.</small>
      </label>

      <label class="board-write__field">
        <span>내용</span>
        <textarea v-model="content" rows="10" placeholder="내용을 입력하세요"></textarea>
      </label>

      <label class="board-write__field">
        <span>{{ isEditMode ? '비밀번호 확인' : '수정용 비밀번호' }}</span>
        <input v-model="password" type="password" placeholder="비밀번호 입력" />
        <small>※ 게시글 수정·삭제 시 확인용으로 사용됩니다 (평문 저장)</small>
      </label>

      <p v-if="errorMessage" class="board-write__error">{{ errorMessage }}</p>

      <div class="board-write__actions">
        <button type="button" class="board-write__cancel-btn" @click="handleCancel">취소</button>
        <button type="submit" class="board-write__submit-btn" :disabled="isSubmitting">등록</button>
      </div>
    </form>
  </section>
</template>

<style scoped>
.board-write__status {
  padding: 2rem 0;
  text-align: center;
  color: var(--color-text-soft);
}

.board-write__form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  margin-top: 1rem;
}

.board-write__card {
  background: var(--color-background);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  padding: 1.5rem;
}

.board-write__field {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.board-write__field span {
  font-weight: var(--weight-semibold);
  font-size: var(--text-sm);
}

.board-write__field input,
.board-write__field textarea {
  padding: 0.65rem 0.9rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-background-soft);
  color: var(--color-text);
  font-family: inherit;
  font-size: var(--text-md);
  resize: vertical;
}

.board-write__field input:focus,
.board-write__field textarea:focus {
  outline: none;
  border-color: var(--color-primary);
  background: var(--color-background);
}

.board-write__field small {
  color: var(--color-text-soft);
  font-size: var(--text-xs);
}

.board-write__error {
  color: var(--color-danger);
  font-size: var(--text-sm);
}

.board-write__actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.board-write__cancel-btn,
.board-write__submit-btn {
  padding: 0.6rem 1.4rem;
  border-radius: var(--radius-full);
  font-weight: 700;
}

.board-write__cancel-btn {
  border: 1px solid var(--color-border);
  background: var(--color-background);
}

.board-write__submit-btn {
  border: none;
  background: var(--color-primary);
  color: #fff;
  box-shadow: var(--shadow-sm);
}

.board-write__submit-btn:not(:disabled):hover {
  background: var(--color-primary-hover);
}

.board-write__submit-btn:disabled {
  opacity: 0.6;
}
</style>
