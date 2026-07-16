<script setup lang="ts">
import { Search } from '@lucide/vue'

defineProps<{
  modelValue: string
  placeholder?: string
}>()

defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>

<template>
  <label class="search-bar">
    <Search class="search-bar__icon" :size="18" />
    <input
      :value="modelValue"
      type="text"
      :placeholder="placeholder"
      autocomplete="off"
      @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
    />
  </label>
</template>

<style scoped>
.search-bar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-full);
  padding: 0.65rem 1.1rem;
  transition: border-color 0.15s ease;
}

.search-bar:focus-within {
  border-color: var(--color-primary);
}

.search-bar__icon {
  flex-shrink: 0;
  color: var(--color-text-soft);
}

.search-bar input {
  flex: 1;
  min-width: 0;
  border: none;
  outline: none;
  background: transparent;
  color: var(--color-text);
  font-size: var(--text-sm);
}
</style>
