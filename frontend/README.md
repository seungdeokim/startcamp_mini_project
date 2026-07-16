# Gumi Log 프론트엔드 (구미/경북)

공공데이터 기반 지역 정보 공유 커뮤니티 **Gumi Log**의 프론트엔드입니다. Vue 3 + TypeScript + Vite로 작성했으며, 당근마켓 톤의 웜 오렌지 브랜드 컬러를 사용합니다.

## 주요 기능

- ✅ **홈** — 그라데이션 히어로 배너, 지역별 실시간 날씨, 바로가기, 최근 게시글
- ✅ **커뮤니티 게시판** — 익명 · 비밀번호 기반 CRUD, 실시간 검색, 페이지네이션
- ✅ **지역정보** — 구미/경북 관광지 목록 · 실시간 검색 · 상세 모달(카카오맵 길찾기 연동)
- ✅ **지도** — Kakao Maps 기반 관광지 마커/클러스터, 핀 라벨, hover 정보 카드, 우측 상단 날씨 배지, "이 근처 관광지" 추천
- ✅ **AI 챗봇** — 전 페이지 우측 하단 플로팅 위젯(`/api/chat` 연동, 날씨·관광지 기반 여행 코스 추천)

## 기술 스택

- **프레임워크**: Vue 3 (`<script setup>`) + TypeScript
- **빌드**: Vite
- **라우팅**: Vue Router
- **지도**: Kakao Maps SDK (동적 로드)
- **아이콘**: `@lucide/vue`
- **폰트**: Pretendard

## 디자인 시스템

전역 토큰은 [`src/assets/base.css`](src/assets/base.css)에 정의되어 있으며, 모든 화면이 이 토큰만 사용해 통일성을 유지합니다.

- **컬러**: 브랜드 오렌지(`--color-primary`) 및 시맨틱 컬러, 라이트/다크 모드 대응
- **타이포 스케일**: `--text-xs`(0.75rem) ~ `--text-2xl`(1.75rem) 6단계 + 웨이트 토큰(`--weight-medium` ~ `--weight-extrabold`)
- **라운드/그림자**: `--radius-*`, `--shadow-*`, 브랜드 그라데이션 `--gradient-brand`
- **공용 컴포넌트**: 검색바([`SearchBar.vue`](src/components/common/SearchBar.vue))는 게시판·지역정보에서 공유합니다.

## 환경변수

`.env.example`을 복사해 `.env`로 만들고 값을 채워주세요. `.env`는 `.gitignore`에 등록되어 있어 커밋되지 않습니다.

| 변수 | 설명 | 기본값 |
| --- | --- | --- |
| `VITE_API_BASE_URL` | 백엔드 API 서버 주소 | `http://localhost:8000` (로컬 개발용, 배포 시 Render 주소로 교체) |
| `VITE_KAKAO_MAP_KEY` | Kakao Maps JavaScript 키(지도 화면용) | (없음) |

## 로컬 실행

백엔드(FastAPI)가 먼저 실행되어 있어야 합니다.

```sh
# 1) 백엔드 (별도 터미널, backend/ 디렉터리에서)
uvicorn main:app --reload

# 2) 프론트엔드
npm install
npm run dev
```

### 프로덕션 빌드 (타입체크 + 번들)

```sh
npm run build
```

### 린트

```sh
npm run lint
```

## 라우트 구조

| 경로 | 설명 |
| --- | --- |
| `/` | 홈(히어로 배너, 날씨, 바로가기, 최근 게시글) |
| `/board` | 게시판 목록 |
| `/board/write` | 게시글 작성 |
| `/board/:id` | 게시글 상세 |
| `/board/:id/edit` | 게시글 수정 |
| `/info` | 지역정보(관광지 목록·상세 모달) |
| `/map` | 지도(관광지 마커·날씨·근처 추천, `fullBleed` 레이아웃) |

## 백엔드 API 연동 메모

- 게시글 수정(`PUT /api/posts/{id}`)은 제목·내용을 **쿼리 파라미터**로, 비밀번호는 **JSON body**(`{ "password": "..." }`)로 전달합니다.
- 게시글 목록/상세 응답에 비밀번호 필드가 포함되어 있으므로 화면에는 절대 표시하지 않습니다.
- 지역정보는 `GET /api/tourist-spots`(구미/경북 관광지 499건, TourAPI 형식)를 그대로 사용합니다.
- 날씨는 `GET /api/weather?region={영문지역명}`, 챗봇은 `POST /api/chat`(`{ "message": "..." }`)를 사용합니다.

## 배포

- Netlify 배포 설정은 저장소 루트의 `netlify.toml`에 정의되어 있습니다(base: `frontend`, publish: `dist`, SPA 리다이렉트 포함).
- 환경변수 `VITE_API_BASE_URL`은 `netlify.toml`의 `[build.environment]`에 Render 백엔드 주소(`https://startcamp-mini-project.onrender.com`)로 설정되어 있습니다.
- `VITE_KAKAO_MAP_KEY`는 Netlify 사이트 환경변수에 별도로 등록해야 지도 화면이 동작합니다.

## 추천 IDE 설정

[VS Code](https://code.visualstudio.com/) + [Vue (Official)](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (Vetur 비활성화)
