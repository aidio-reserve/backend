from sqlalchemy.orm import Session
from datetime import datetime
from ..models.models import ChatHistory


def add_chat_history(db: Session, user_id: str, message: str) -> ChatHistory:
    """
    新しい会話履歴をデータベースに追加する。
    """
    chat_history = ChatHistory(
        user_id=user_id, message=message, created_at=datetime.utcnow()
    )
    db.add(chat_history)
    db.commit()
    db.refresh(chat_history)
    return chat_history


def get_chat_history(db: Session, user_id: str):
    """
    特定のユーザーIDに紐づく会話履歴をすべて取得する。
    """
    return db.query(ChatHistory).filter(ChatHistory.user_id == user_id).all()
