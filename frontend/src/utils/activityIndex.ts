export type ActivityLevel = 'danger' | 'warning' | 'info' | 'success'

export interface ActivityIndex {
  text: string
  level: ActivityLevel
}

export function calculateActivityIndex(temp: number, humidity: number, weather: string): ActivityIndex {
  if (temp > 33 || temp < -5) {
    return { text: '매우 더움/추움 (실내 관광 권장)', level: 'danger' }
  }
  if (humidity > 80 && temp > 25) {
    return { text: '습하고 무더움 (열대야 주의)', level: 'warning' }
  }
  if (weather && (weather.includes('비') || weather.includes('눈') || weather.includes('흐림'))) {
    return { text: '실내 활동 또는 우산 지참', level: 'info' }
  }
  return { text: '매우 쾌적함 (나들이 최적)', level: 'success' }
}
