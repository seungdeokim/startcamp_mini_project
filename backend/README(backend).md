```markdown
# 🌐 LocalHub Backend API

구미 및 경북권 지역 커뮤니티와 스마트 관광 안내를 제공하는 **LocalHub** 프로젝트의 백엔드 서버입니다. FastAPI와 SQLite를 기반으로 가볍고 빠르게 동작하며, 외부 API(OpenWeather, OpenAI 등)와 연동되어 있습니다.

---

## 🛠 Tech Stack

* **Language**: Python 3.10+
* **Framework**: FastAPI
* **Database**: SQLite & SQLAlchemy (ORM)
* **AI & External APIs**: OpenAI API, Google Gemini API, OpenWeatherMap API
* **Environment Management**: python-dotenv, Pydantic

---

## 📂 Project Structure

```text
backend/
├── main.py                  # FastAPI 앱 메인 엔트리포인트 및 라우터 정의
├── 구미_경북권_관광지.json       # 지역 관광지 오픈 데이터 (JSON)
├── localhub.db              # SQLite 로컬 데이터베이스 파일
└── .env                     # 환경 변수 설정 파일 (Git 제외)

```

---

## 🚀 Getting Started (설치 및 실행 방법)

### 1. 사전 준비 사항

* Python 3.10 이상이 설치되어 있어야 합니다.

### 2. 저장소 클론 및 폴더 이동

```bash
git clone [https://github.com/seungdeokim/startcamp_mini_project.git](https://github.com/seungdeokim/startcamp_mini_project.git)
cd "startcamp project/backend"

```

### 3. 가상환경 생성 및 활성화

* **Windows (PowerShell)**:
```bash
python -m venv venv
venv\Scripts\Activate

```


* **Mac / Linux**:
```bash
python3 -m venv venv
source venv/bin/activate

```



### 4. 패키지 의존성 설치

```bash
pip install fastapi uvicorn sqlalchemy pydantic requests python-dotenv google-genai openai

```

### 5. 환경 변수(`.env`) 설정

`backend` 폴더 내부에 `.env` 파일을 생성하고 아래 키값들을 설정해 주세요.

```env
WEATHER_API_KEY=당신의_OpenWeatherMap_API_키
OPENAI_API_KEY=당신의_OpenAI_API_키
GEMINI_API_KEY=당신의_Gemini_API_키

```

### 6. 서버 실행

```bash
uvicorn main:app --reload

```

* 서버가 정상 실행되면 브라우저에서 아래 주소로 접속하여 API 문서를 확인할 수 있습니다:
* **Swagger UI (API 테스트)**: `http://127.0.0.1:8000/docs`
* **ReDoc**: `http://127.0.0.1:8000/redoc`



---

## 📌 API Endpoints

### 1. Root

* `GET /` : 서버 실행 상태 확인

### 2. 커뮤니티 게시판 (`/api/posts`)

* `GET /api/posts` : 전체 게시글 목록 조회
* `POST /api/posts` : 새로운 익명 게시글 작성
* `GET /api/posts/{post_id}` : 특정 게시글 상세 조회
* `PUT /api/posts/{post_id}` : 게시글 수정 (비밀번호 인증)
* `DELETE /api/posts/{post_id}` : 게시글 삭제 (비밀번호 인증)

### 3. 지역 정보 및 외부 API (`/api`)

* `GET /api/tourist-spots` : 구미 및 경북권 관광지 정보 목록 조회
* `GET /api/weather?region={지역명}` : OpenWeatherMap 연동 실시간 날씨 정보 조회
* `POST /api/chat` : AI 기반 지역 관광 코스 추천 및 여행 도우미 챗봇 API

```

```