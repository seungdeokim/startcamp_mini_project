import json
import os
import requests
import random
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from google import genai

# 환경변수 파일(.env) 로드
load_dotenv()

# Gemini 클라이언트 초기화 (.env의 GEMINI_API_KEY 자동 인식)
gemini_api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=gemini_api_key) if gemini_api_key and gemini_api_key != "여기에_발급받은_Gemini_API_키" else None

# ==========================================
# 1. 데이터베이스 설정 (SQLite)
# ==========================================
SQLALCHEMY_DATABASE_URL = "sqlite:///./localhub.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==========================================
# 2. 데이터베이스 및 Pydantic 모델 설계
# ==========================================
class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    author = Column(String(50), default="ㅇㅇ")
    password = Column(String(4), nullable=False)
    category = Column(String(50), default="일반")  # 카테고리 필드 하나만 유지

class PostCreate(BaseModel):
    title: str
    content: str
    author: str = "ㅇㅇ"
    password: str
    category: str = "일반"  # 프론트엔드가 안 보내도 기본 "일반"으로 들어가게 설정

class PostAction(BaseModel):
    password: str

# 테이블 자동 생성
Base.metadata.create_all(bind=engine)

app = FastAPI(title="LocalHub API", description="익명 커뮤니티 및 관광/날씨/Gemini API")

# 프론트엔드 연동을 위한 CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB 세션 의존성 주입 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==========================================
# 3. API 엔드포인트 (라우터)
# ==========================================
@app.get("/")
def read_root():
    return {"message": "LocalHub 백엔드 서버가 정상적으로 실행 중입니다!"}

@app.post("/api/posts", status_code=201)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    new_post = Post(
        title=post.title,
        content=post.content,
        author=post.author,
        password=post.password,
        category=post.category
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"message": "게시글이 작성되었습니다.", "post_id": new_post.id}

@app.get("/api/posts")
def get_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    posts = db.query(Post).offset(skip).limit(limit).all()
    return posts

@app.get("/api/posts/{post_id}")
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    return post

@app.put("/api/posts/{post_id}")
def update_post(post_id: int, action: PostAction, title: str, content: str, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    if post.password != action.password:
        raise HTTPException(status_code=403, detail="비밀번호가 일치하지 않습니다.")
        
    post.title = title
    post.content = content
    db.commit()
    return {"message": "게시글이 수정되었습니다."}

@app.delete("/api/posts/{post_id}")
def delete_post(post_id: int, action: PostAction, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    if post.password != action.password:
        raise HTTPException(status_code=403, detail="비밀번호가 일치하지 않습니다.")
        
    db.delete(post)
    db.commit()
    return {"message": "게시글이 삭제되었습니다."}

@app.get("/api/tourist-spots")
def get_tourist_spots():
    file_path = "구미_경북권_관광지.json"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="관광지 데이터 파일을 찾을 수 없습니다.")
        
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    return data.get("items", [])

REGION_MAPPING = {
    "구미": "Gumi",
    "대구": "Daegu",
    "김천": "Gimcheon",
    "상주": "Sangju",
    "칠곡": "Chilgok",
    "고령": "Daegu",
    "성주": "Daegu",
    "경산": "Gyeongsan",
    "안동": "Andong",
    "포항": "Pohang",
    "경주": "Gyeongju"
}

def resolve_region(text: str) -> str:
    if text in ["Gumi", "Daegu", "Gimcheon", "Sangju", "Chilgok"]:
        return text
    for korean_name, eng_name in REGION_MAPPING.items():
        if korean_name in text:
            return eng_name
    return "Gumi"

def fetch_weather_data(region: str) -> dict:
    api_key = os.getenv("WEATHER_API_KEY")
    target_region = resolve_region(region)

    if not api_key or api_key == "여기에_실제_API_키를_입력하세요":
        return {
            "region": region,
            "weather": "맑음",
            "temp": 28.5,
            "humidity": 55,
            "note": "API 키가 설정되지 않아 임시 데이터를 반환합니다."
        }

    url = f"http://api.openweathermap.org/data/2.5/weather?q={target_region}&appid={api_key}&units=metric&lang=kr"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        return {
            "region": region,
            "weather": data["weather"][0]["description"],
            "temp": data["main"]["temp"],
            "humidity": data["main"]["humidity"]
        }
    raise HTTPException(status_code=response.status_code, detail="날씨 정보를 가져오는 데 실패했습니다.")

@app.get("/api/weather")
def get_weather(region: str = "Gumi"):
    try:
        return fetch_weather_data(region)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# OpenAI API 연동 챗봇 라우터
# ==========================================
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

@app.post("/api/chat", response_model=ChatResponse)
def chat_bot(request: ChatRequest):
    try:
        file_path = "구미_경북권_관광지.json"
        spots_info = ""
        msg = request.message
        
        region = resolve_region(msg)

        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)
                items = json_data.get("items", [])

                # 1. 질문에 관광지 이름이 직접 언급됐으면 그것부터 우선 매칭
                relevant_spots = [s for s in items if s.get('title') and s.get('title') in msg]

                # 2. 이름 매칭이 없으면 질문에서 유추한 지역(addr1)으로 매칭
                if not relevant_spots:
                    region_keyword = next((k for k in REGION_MAPPING if k in msg), None)
                    if region_keyword:
                        relevant_spots = [s for s in items if region_keyword in s.get('addr1', '')]

                # 3. 그래도 없으면 전체에서 랜덤으로 추출 (토큰 절약 및 다양성 확보)
                if not relevant_spots:
                    relevant_spots = random.sample(items, min(4, len(items))) if items else []
                else:
                    relevant_spots = random.sample(relevant_spots, min(4, len(relevant_spots)))

                # 보기 좋게 문자열로 포맷팅
                spots_info = "\n".join([f"- {s.get('title')} ({s.get('addr1', '주소 미상')})" for s in relevant_spots])

        try:
            weather = fetch_weather_data(region)
            weather_info = f"{weather['weather']}, 기온 {weather['temp']}°C, 습도 {weather['humidity']}%"
        except Exception:
            weather_info = "정보 없음"

        current_api_key = os.getenv("OPENAI_API_KEY")

        prompt = f"""
        [오늘 {region} 날씨]
        {weather_info}

        [추천 관광지 정보]
        {spots_info}

        [질문]
        {msg}
        """

        if current_api_key:
            from openai import OpenAI
            openai_client = OpenAI(api_key=current_api_key)

            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.7,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "너는 구미 및 경북권 스마트 관광 도우미 '로컬허브 AI'야. "
                            "제공된 날씨와 추천 관광지 정보를 참고해서 실제로 방문할 만한 구체적인 코스를 추천해줘. "
                            "관광지 이름은 굵게 강조하고, 여러 곳을 추천할 땐 목록으로 정리해줘. "
                            "날씨가 좋지 않으면 실내 위주로, 화창하면 야외 위주로 추천해줘. "
                            "정보에 없는 내용은 지어내지 말고, 대신 아는 선에서 일반적인 여행 팁으로 답해줘. "
                            "답변 끝에는 짧은 후속 질문을 자연스럽게 덧붙여줘."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            reply_text = response.choices[0].message.content
        else:
            reply_text = "[LocalHub AI] .env 파일에 OPENAI_API_KEY가 설정되지 않았습니다."

        return {"reply": reply_text}
        
    except Exception as e:
        return {"reply": f"[안내] 질문에 대해 처리하는 동안 오류가 발생했습니다: {str(e)}"}