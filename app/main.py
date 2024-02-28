from fastapi import FastAPI
from .api.v1 import chat_router
from .core.config import settings
from .database import engine, Base

# データベーステーブルの作成 (SQLAlchemyを使用している場合)
Base.metadata.create_all(bind=engine)

app = FastAPI()

# ルーターのマウント
app.include_router(chat_router.router, prefix="/api/v1/chat", tags=["chat"])


# ルートパスへのリクエストに対するレスポンスの定義
@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the chat API!"}
