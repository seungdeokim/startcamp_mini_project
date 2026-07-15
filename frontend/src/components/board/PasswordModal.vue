<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  visible: boolean
  errorMessage?: string
  isSubmitting?: boolean
}>()

const emit = defineEmits<{
  confirm: [password: string]
  cancel: []
}>()

const password = ref('')

watch(
  () => props.visible,
  (visible) => {
    if (visible) password.value = ''
  },
)

function handleConfirm() {
  if (!password.value) return
  emit('confirm', password.value)
}
</script>

<template>
  <div v-if="visible" class="password-modal__backdrop" @click.self="emit('cancel')">
    <div class="password-modal">
      <h2>비밀번호 확인</h2>
      <input
        v-model="password"
        type="password"
        placeholder="수정용 비밀번호 입력"
        class="password-modal__input"
        @keyup.enter="handleConfirm"
      />
      <p v-if="errorMessage" class="password-modal__error">{{ errorMessage }}</p>
      <button type="button" class="password-modal__confirm" :disabled="isSubmitting" @click="handleConfirm">
        확인
      </button>
    </div>
  </div>
</template>

<style scoped>
.password-modal__backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 30;
}

.password-modal {
  background: var(--color-background);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  width: min(320px, 90vw);
  text-align: center;
  box-shadow: var(--shadow-lg);
}

.password-modal h2 {
  font-size: 1.05rem;
  margin-bottom: 1rem;
}

.password-modal__input {
  width: 100%;
  padding: 0.65rem 0.9rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-background-soft);
  color: var(--color-text);
  margin-bottom: 0.5rem;
}

.password-modal__input:focus {
  outline: none;
  border-color: var(--color-primary);
  background: var(--color-background);
}

.password-modal__error {
  color: var(--color-danger);
  font-size: 0.85rem;
  margin-bottom: 0.5rem;
}

.password-modal__confirm {
  width: 100%;
  padding: 0.65rem 0.75rem;
  border-radius: var(--radius-full);
  border: none;
  background: var(--color-primary);
  color: #fff;
  font-weight: 700;
}

.password-modal__confirm:not(:disabled):hover {
  background: var(--color-primary-hover);
}

.password-modal__confirm:disabled {
  opacity: 0.6;
}
</style>
