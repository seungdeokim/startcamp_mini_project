import { apiClient } from './client'
import type { WeatherInfo } from '@/types/weather'

export function getWeather(region: string) {
  return apiClient.get<WeatherInfo>(`/api/weather?region=${encodeURIComponent(region)}`)
}
