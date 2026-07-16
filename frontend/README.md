# Gumi Log 프론트엔드 (구미/경북)

공공데이터 기반 지역 정보 공유 커뮤니티 Gumi Log의 프론트엔드(Vue 3 + TypeScript + Vite)입니다.

## 현재 구현 범위

- ✅ 커뮤니티 게시판(익명, 비밀번호 기반 CRUD)
- ✅ 지역정보(구미/경북 관광지 목록·검색·상세)
- ⏳ 챗봇 위젯, 지도 시각화(Kakao Maps), 날씨 연동 — 다음 단계 예정

## 환경변수

`.env.example`을 복사해 `.env`로 만들고 값을 채워주세요. `.env`는 `.gitignore`에 등록되어 있어 커밋되지 않습니다.

| 변수 | 설명 | 기본값 |
| --- | --- | --- |
| `VITE_API_BASE_URL` | 백엔드 API 서버 주소 | `http://localhost:8000` (로컬 개발용, 배포 시 Render 주소로 교체) |

## 로컬 실행

백엔드(FastAPI)가 먼저 실행되어 있어야 합니다.

```sh
# 1) 백엔드 (별도 터미널, backend/ 디렉터리에서)
uvicorn main:app --reload

# 2) 프론트엔드
npm install
npm run dev
```

### Type-Check, Compile and Minify for Production

```sh
npm run build
```

### Lint with [ESLint](https://eslint.org/)

```sh
npm run lint
```

## 라우트 구조

| 경로 | 설명 |
| --- | --- |
| `/` | 홈(배너, 바로가기, 최근 게시글) |
| `/board` | 게시판 목록 |
| `/board/write` | 게시글 작성 |
| `/board/:id` | 게시글 상세 |
| `/board/:id/edit` | 게시글 수정 |
| `/info` | 지역정보(관광지 목록) |

## 백엔드 API 연동 메모

- 게시글 수정(`PUT /api/posts/{id}`)은 제목·내용을 **쿼리 파라미터**로, 비밀번호는 **JSON body**(`{ "password": "..." }`)로 전달합니다.
- 게시글 목록/상세 응답에 비밀번호 필드가 포함되어 있으므로 화면에는 절대 표시하지 않습니다.
- 지역정보는 `GET /api/tourist-spots`(구미/경북 관광지 499건, TourAPI 형식)를 그대로 사용합니다.

## 배포

- Netlify 배포 설정은 저장소 루트의 `netlify.toml`에 정의되어 있습니다(base: `frontend`, publish: `dist`, SPA 리다이렉트 포함).
- 환경변수 `VITE_API_BASE_URL`은 `netlify.toml`의 `[build.environment]`에 Render 백엔드 주소(`https://startcamp-mini-project.onrender.com`)로 설정되어 있습니다.

## 추천 IDE 설정

[VS Code](https://code.visualstudio.com/) + [Vue (Official)](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (Vetur 비활성화)
