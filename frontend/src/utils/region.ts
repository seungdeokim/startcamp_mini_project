// 관광지 주소 문자열에서 날씨 API(GET /api/weather?region=)에 넘길 영문 지역명을 추출한다.
// 제공 데이터가 구미/경북 권역이므로 인접 시군 위주로만 판별하고, 기본값은 구미로 둔다.
export function extractRegionFromAddress(addr1: string): string {
  if (addr1.includes('대구')) return 'Daegu'
  if (addr1.includes('김천')) return 'Gimcheon'
  if (addr1.includes('상주')) return 'Sangju'
  if (addr1.includes('칠곡')) return 'Chilgok'
  return 'Gumi'
}
