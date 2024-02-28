from fastapi import APIRouter, HTTPException, Body, Depends
from sqlalchemy.orm import Session
from typing import List

from ..crud.chat_crud import add_chat_history, get_chat_history
from ..database import get_db
from ..models.models import ChatHistory
from ..schemas.chat_schema import ChatMessageCreate, ChatMessage
from ..services.chat_service import get_response

router = APIRouter()


@router.post("/message/", response_model=ChatMessage)
async def send_message(message: ChatMessageCreate, db: Session = Depends(get_db)):
    # ユーザーからのメッセージを会話履歴に追加
    chat_message = add_chat_history(
        db=db, user_id=message.user_id, message=message.message
    )

    # AIからの返答を取得
    response = get_response(message.message)

    # AIの返答も会話履歴に追加
    add_chat_history(db=db, user_id="AI", message=response)

    return {
        "user_id": chat_message.user_id,
        "message": chat_message.message,
        "created_at": chat_message.created_at,
        "response": response,
    }


@router.get("/history/{user_id}", response_model=List[ChatMessage])
async def read_chat_history(user_id: str, db: Session = Depends(get_db)):
    # 指定されたユーザーIDの会話履歴を取得
    history = get_chat_history(db=db, user_id=user_id)
    if not history:
        raise HTTPException(status_code=404, detail="Chat history not found")
    return history
