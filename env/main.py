from fastapi import FastAPI, UploadFile,File,WebSocket,Request,Depends

from models.database import SessionLocal, engine, Base
from sqlalchemy.orm import Session

from services.uploadspdf import uploadfile
from services.websocket import handlewebsocket
from ratelimiting.ratelimiting import RateLimitMiddleware

from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


Settings.llm = None 
# Configure LlamaIndex settings
Settings.embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

app = FastAPI()
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    middleware = RateLimitMiddleware(app)
    return await middleware(request, call_next)


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/uploadpdf")
async def uploadpdf(file: UploadFile = File(...)):
    return uploadfile(file)


@app.websocket("/ws/{filename}")
async def websocket_endpoint(websocket: WebSocket, filename: str):
    return await handlewebsocket(websocket,filename)