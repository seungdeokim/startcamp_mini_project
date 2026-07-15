import { apiClient } from './client'
import type { Post, PostCreatePayload } from '@/types/post'

export function getPosts() {
  return apiClient.get<Post[]>('/api/posts')
}

export function getPost(id: number) {
  return apiClient.get<Post>(`/api/posts/${id}`)
}

export function createPost(payload: PostCreatePayload) {
  return apiClient.post<{ message: string; post_id: number }>('/api/posts', payload)
}

export function updatePost(id: number, title: string, content: string, password: string) {
  const query = new URLSearchParams({ title, content }).toString()
  return apiClient.put<{ message: string }>(`/api/posts/${id}?${query}`, { password })
}

export function deletePost(id: number, password: string) {
  return apiClient.del<{ message: string }>(`/api/posts/${id}`, { password })
}
