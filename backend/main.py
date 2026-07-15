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
    category = Column(String, nullable=False, default="구미경북")
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    author = Column(String(50), default="ㅇㅇ")
    password = Column(String(4), nullable=False)
    category = Column(String(50), default="일반")  # 카테고리 기본값 추가

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
        category="구미경북",
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

@app.get("/api/weather")
def get_weather(region: str = "Gumi"):
    api_key = os.getenv("WEATHER_API_KEY")
    
    # 고령, 성주 등 군 단위 지역을 OpenWeatherMap이 인식하는 인근 대도시 명칭으로 매핑
    region_mapping = {
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
    
    target_region = "Gumi"
    for korean_name, eng_name in region_mapping.items():
        if korean_name in region:
            target_region = eng_name
            break
            
    if region in ["Gumi", "Daegu", "Gimcheon", "Sangju", "Chilgok"]:
        target_region = region

    if not api_key or api_key == "여기에_실제_API_키를_입력하세요":
        return {
            "region": region, 
            "weather": "맑음", 
            "temp": 28.5,
            "humidity": 55,
            "note": "API 키가 설정되지 않아 임시 데이터를 반환합니다."
        }
        
    url = f"http://api.openweathermap.org/data/2.5/weather?q={target_region}&appid={api_key}&units=metric&lang=kr"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            return {
                "region": region,
                "weather": data["weather"][0]["description"],
                "temp": data["main"]["temp"],
                "humidity": data["main"]["humidity"]
            }
        else:
            raise HTTPException(status_code=response.status_code, detail="날씨 정보를 가져오는 데 실패했습니다.")
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
        # 1. 로컬 관광지 데이터 읽어오기
        file_path = "구미_경북권_관광지.json"
        spots_info = ""
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)
                items = json_data.get("items", [])
                spots_info = ", ".join([f"{s.get('title')}({s.get('addr1', '')})" for s in items[:20]])

        msg = request.message

        # 💡 [핵심 수정] 함수 내부에서 환경 변수를 직접 확인하여 변수 없음(NameError) 에러 차단
        current_api_key = os.getenv("OPENAI_API_KEY")

        # 2. AI에게 전달할 프롬프트 구성
        prompt = f"""
        너는 구미 및 경북권 스마트 관광 도우미야. 
        아래 참고용 지역 관광지 데이터와 사용자의 질문을 바탕으로 친절하고 유익한 여행 추천 및 안내 답변을 작성해줘.
        
        [참고 관광지 목록]
        {spots_info}
        
        [사용자 질문]
        {msg}
        """
        
        # 3. OpenAI API 호출
        if current_api_key:
            # 안전하게 여기서 클라이언트 객체 생성
            from openai import OpenAI
            client = OpenAI(api_key=current_api_key)
            
            response = client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful travel assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            reply_text = response.choices[0].message.content
        else:
            reply_text = "[LocalHub AI] .env 파일에 OPENAI_API_KEY가 설정되지 않았습니다."

        return {"reply": reply_text}
        
    except Exception as e:
        return {"reply": f"[안내] 질문에 대해 처리하는 동안 오류가 발생했습니다: {str(e)}"}