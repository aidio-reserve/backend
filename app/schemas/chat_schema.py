from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ChatMessageCreate(BaseModel):
    """
    ユーザーからのメッセージ入力用スキーマ
    """

    user_id: str
    message: str


class ChatMessage(BaseModel):
    """
    チャットメッセージ出力用スキーマ
    """

    id: int
    user_id: str
    message: str
    created_at: datetime

    class Config:
        orm_mode = True


class ChatHistoryResponse(BaseModel):
    """
    チャット履歴の出力用スキーマ
    """

    user_id: str
    messages: list[ChatMessage]


class AIResponse(BaseModel):
    """
    AIからの返答用スキーマ
    """

    response: str
    created_at: datetime = datetime.now()
