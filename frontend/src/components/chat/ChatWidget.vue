<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import { MessageCircle, Sparkles, Send, X } from '@lucide/vue'
import { postChat } from '@/api/chat'
import { ApiError } from '@/api/client'
import type { ChatMessage } from '@/types/chat'

const isOpen = ref(false)
const isLoading = ref(false)
const draft = ref('')
const messages = ref<ChatMessage[]>([])
const listEl = ref<HTMLElement | null>(null)

const suggestions = ['오늘 구미 날씨 어때?', '경북권 여행 코스 추천해줘', '가족이랑 갈만한 곳 알려줘']

const canSend = computed(() => draft.value.trim().length > 0 && !isLoading.value)

function toggleOpen() {
  isOpen.value = !isOpen.value
}

function scrollToBottom() {
  nextTick(() => {
    if (listEl.value) {
      listEl.value.scrollTop = listEl.value.scrollHeight
    }
  })
}

watch(messages, scrollToBottom, { deep: true })

async function sendMessage(text?: string) {
  const content = (text ?? draft.value).trim()
  if (!content || isLoading.value) return

  messages.value.push({ role: 'user', content })
  draft.value = ''
  isLoading.value = true
  scrollToBottom()

  try {
    const { reply } = await postChat(content)
    messages.value.push({ role: 'assistant', content: reply })
  } catch (e) {
    const detail = e instanceof ApiError ? e.message : '네트워크 연결을 확인해 주세요.'
    messages.value.push({
      role: 'assistant',
      content: `앗, 답변을 가져오지 못했어요. (${detail})`,
    })
  } finally {
    isLoading.value = false
  }
}

function escapeHtml(str: string) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

function formatMessage(content: string) {
  const escaped = escapeHtml(content)
  const bolded = escaped.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  return bolded.replace(/\n/g, '<br>')
}
</script>

<template>
  <div class="chat-widget">
    <Transition name="chat-panel">
      <div v-if="isOpen" class="chat-panel">
        <header class="chat-panel__header">
          <div class="chat-panel__avatar">
            <Sparkles :size="18" />
          </div>
          <div class="chat-panel__heading">
            <p class="chat-panel__title">Gumi Log AI</p>
            <p class="chat-panel__subtitle">구미·경북 여행 도우미</p>
          </div>
          <button type="button" class="chat-panel__close" aria-label="챗봇 닫기" @click="toggleOpen">
            <X :size="18" />
          </button>
        </header>

        <div ref="listEl" class="chat-panel__body">
          <div v-if="messages.length === 0" class="chat-welcome">
            <div class="chat-panel__avatar chat-panel__avatar--lg">
              <Sparkles :size="22" />
            </div>
            <p class="chat-welcome__text">
              안녕하세요! 구미·경북권 날씨와 관광지 정보를 바탕으로<br />여행 코스를 추천해드려요.
            </p>
            <div class="chat-welcome__suggestions">
              <button
                v-for="s in suggestions"
                :key="s"
                type="button"
                class="chat-chip"
                @click="sendMessage(s)"
              >
                {{ s }}
              </button>
            </div>
          </div>

          <div
            v-for="(m, i) in messages"
            :key="i"
            class="chat-bubble-row"
            :class="`chat-bubble-row--${m.role}`"
          >
            <div v-if="m.role === 'assistant'" class="chat-panel__avatar chat-panel__avatar--sm">
              <Sparkles :size="14" />
            </div>
            <div class="chat-bubble" :class="`chat-bubble--${m.role}`" v-html="formatMessage(m.content)" />
          </div>

          <div v-if="isLoading" class="chat-bubble-row chat-bubble-row--assistant">
            <div class="chat-panel__avatar chat-panel__avatar--sm">
              <Sparkles :size="14" />
            </div>
            <div class="chat-bubble chat-bubble--assistant chat-bubble--typing">
              <span></span><span></span><span></span>
            </div>
          </div>
        </div>

        <form class="chat-panel__input" @submit.prevent="sendMessage()">
          <input
            v-model="draft"
            type="text"
            placeholder="궁금한 여행 정보를 물어보세요"
            :disabled="isLoading"
            autocomplete="off"
          />
          <button type="submit" class="chat-panel__send" :disabled="!canSend" aria-label="전송">
            <Send :size="16" />
          </button>
        </form>
      </div>
    </Transition>

    <button
      type="button"
      class="chat-fab"
      :class="{ 'chat-fab--open': isOpen }"
      :aria-label="isOpen ? '챗봇 닫기' : '챗봇 열기'"
      @click="toggleOpen"
    >
      <Transition name="chat-fab-icon" mode="out-in">
        <X v-if="isOpen" key="close" :size="24" />
        <MessageCircle v-else key="open" :size="24" />
      </Transition>
      <span v-if="!isOpen" class="chat-fab__badge">AI</span>
    </button>
  </div>
</template>

<style scoped>
.chat-widget {
  position: fixed;
  right: 1.1rem;
  bottom: calc(1.1rem + env(safe-area-inset-bottom, 0px));
  z-index: 60;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.chat-fab {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-full);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-hover));
  box-shadow: var(--shadow-lg);
  cursor: pointer;
  position: relative;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
}

.chat-fab:hover {
  transform: translateY(-2px) scale(1.04);
  box-shadow: 0 14px 32px rgba(255, 126, 54, 0.35);
}

.chat-fab:active {
  transform: scale(0.96);
}

.chat-fab--open {
  background: var(--color-text-soft);
}

.chat-fab__badge {
  position: absolute;
  top: -4px;
  left: -4px;
  background: var(--color-secondary);
  color: #fff;
  font-size: 0.55rem;
  font-weight: 800;
  line-height: 1;
  padding: 0.25rem 0.35rem;
  border-radius: var(--radius-full);
  box-shadow: 0 0 0 2px var(--color-background);
}

.chat-fab-icon-enter-active,
.chat-fab-icon-leave-active {
  transition: all 0.15s ease;
}

.chat-fab-icon-enter-from,
.chat-fab-icon-leave-to {
  opacity: 0;
  transform: rotate(-45deg) scale(0.6);
}

.chat-panel {
  margin-bottom: 0.75rem;
  width: min(360px, calc(100vw - 2.2rem));
  height: min(520px, calc(100vh - 8rem));
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-panel-enter-active,
.chat-panel-leave-active {
  transition:
    opacity 0.18s ease,
    transform 0.18s ease;
}

.chat-panel-enter-from,
.chat-panel-leave-to {
  opacity: 0;
  transform: translateY(12px) scale(0.96);
  transform-origin: bottom right;
}

.chat-panel__header {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.85rem 0.9rem;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-primary-soft);
}

.chat-panel__avatar {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-hover));
}

.chat-panel__avatar--sm {
  width: 24px;
  height: 24px;
}

.chat-panel__avatar--lg {
  width: 44px;
  height: 44px;
  margin: 0 auto 0.75rem;
}

.chat-panel__heading {
  flex: 1;
  min-width: 0;
}

.chat-panel__title {
  font-size: var(--text-md);
  font-weight: var(--weight-extrabold);
  color: var(--color-heading);
}

.chat-panel__subtitle {
  font-size: var(--text-xs);
  color: var(--color-text-soft);
}

.chat-panel__close {
  border: none;
  background: transparent;
  color: var(--color-text-soft);
  cursor: pointer;
  padding: 0.25rem;
  display: flex;
}

.chat-panel__body {
  flex: 1;
  overflow-y: auto;
  padding: 0.9rem;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  background: var(--color-background-soft);
}

.chat-welcome {
  text-align: center;
  padding: 1rem 0.5rem;
  margin: auto 0;
}

.chat-welcome__text {
  font-size: var(--text-sm);
  color: var(--color-text-soft);
  line-height: 1.5;
  margin-bottom: 0.9rem;
}

.chat-welcome__suggestions {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.chat-chip {
  border: 1px solid var(--color-border);
  background: var(--color-background);
  color: var(--color-text);
  border-radius: var(--radius-full);
  padding: 0.5rem 0.9rem;
  font-size: var(--text-xs);
  cursor: pointer;
  transition:
    background 0.15s ease,
    border-color 0.15s ease;
}

.chat-chip:hover {
  border-color: var(--color-primary);
  background: var(--color-primary-soft);
  color: var(--color-primary-hover);
}

.chat-bubble-row {
  display: flex;
  align-items: flex-end;
  gap: 0.4rem;
  max-width: 100%;
}

.chat-bubble-row--user {
  justify-content: flex-end;
}

.chat-bubble {
  max-width: 78%;
  padding: 0.55rem 0.8rem;
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  line-height: 1.55;
  white-space: normal;
  word-break: break-word;
}

.chat-bubble--user {
  background: var(--color-primary);
  color: #fff;
  border-bottom-right-radius: 4px;
}

.chat-bubble--assistant {
  background: var(--color-background);
  border: 1px solid var(--color-border);
  color: var(--color-text);
  border-bottom-left-radius: 4px;
}

.chat-bubble--typing {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.75rem 0.9rem;
}

.chat-bubble--typing span {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--color-text-soft);
  animation: chat-typing 1.1s infinite ease-in-out;
}

.chat-bubble--typing span:nth-child(2) {
  animation-delay: 0.15s;
}

.chat-bubble--typing span:nth-child(3) {
  animation-delay: 0.3s;
}

@keyframes chat-typing {
  0%,
  60%,
  100% {
    opacity: 0.3;
    transform: translateY(0);
  }
  30% {
    opacity: 1;
    transform: translateY(-3px);
  }
}

.chat-panel__input {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.7rem;
  border-top: 1px solid var(--color-border);
  background: var(--color-background);
}

.chat-panel__input input {
  flex: 1;
  min-width: 0;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-full);
  padding: 0.55rem 0.9rem;
  font-size: var(--text-sm);
  color: var(--color-text);
  background: var(--color-background-soft);
}

.chat-panel__input input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.chat-panel__send {
  flex-shrink: 0;
  width: 34px;
  height: 34px;
  border-radius: var(--radius-full);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  background: var(--color-primary);
  cursor: pointer;
  transition:
    opacity 0.15s ease,
    transform 0.15s ease;
}

.chat-panel__send:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.chat-panel__send:not(:disabled):hover {
  transform: scale(1.06);
}

@media (max-width: 720px) {
  .chat-widget {
    right: 0.8rem;
    bottom: calc(3.5rem + 0.8rem + env(safe-area-inset-bottom, 0px));
  }

  .chat-panel {
    width: calc(100vw - 1.6rem);
    height: min(70vh, 560px);
  }
}
</style>
