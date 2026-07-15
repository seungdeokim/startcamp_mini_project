import { apiClient } from './client'
import type { TouristSpot } from '@/types/tourist'

export function getTouristSpots() {
  return apiClient.get<TouristSpot[]>('/api/tourist-spots')
}
