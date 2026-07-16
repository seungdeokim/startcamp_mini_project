import { apiClient } from './client'
import type { ChatResponse } from '@/types/chat'

export function postChat(message: string) {
  return apiClient.post<ChatResponse>('/api/chat', { message })
}
