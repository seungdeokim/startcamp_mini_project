// 마커를 지도용 핀(물방울) 이미지로 렌더링하기 위한 인라인 SVG 생성기.
// 선택 여부에 따라 크기와 색상만 다른 두 가지 이미지를 만든다.
export function createMarkerImage(active: boolean) {
  const width = active ? 28 : 20
  const height = active ? 36 : 26
  const fill = active ? '#ff7e36' : '#212529'
  const svg =
    `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 32 42">` +
    `<path d="M16 0C7.163 0 0 7.163 0 16c0 10.7 13.2 24 15.3 26a1 1 0 0 0 1.4 0C18.8 40 32 26.7 32 16 32 7.163 24.837 0 16 0z" fill="${fill}"/>` +
    `<circle cx="16" cy="16" r="6.5" fill="#ffffff"/>` +
    `</svg>`
  const uri = `data:image/svg+xml;base64,${btoa(svg)}`

  return new window.kakao.maps.MarkerImage(uri, new window.kakao.maps.Size(width, height), {
    offset: new window.kakao.maps.Point(width / 2, height),
  })
}
