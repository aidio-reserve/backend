from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
from ... import settings

Base = declarative_base()


class ChatHistory(Base):
    __tablename__ = "chat_history"

    # 各メッセージの一意のID
    id = Column(Integer, primary_key=True, autoincrement=True)

    # メッセージを送信したユーザーのID
    user_id = Column(String(255), nullable=False)

    # メッセージの内容
    message = Column(String(255), nullable=False)

    # メッセージが作成された日時
    created_at = Column(DateTime, default=datetime.utcnow)


DATABASE_URL = settings.DATABASE_URL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)
