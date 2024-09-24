from google.cloud import firestore
from langchain_google_firestore import FirestoreChatMessageHistory

# 認証情報はデフォルトの認証情報を利用する
client = firestore.Client(project="aidio-reserve")

def save_ai_message(thread_id, message):
    # FirestoreChatMessageHistoryの初期化
    chat_history = FirestoreChatMessageHistory(
        session_id = thread_id,
        collection = "threads",
        client = client
    )
    chat_history.add_ai_message(message)

def save_user_message(thread_id, message):
    # FirestoreChatMessageHistoryの初期化
    chat_history = FirestoreChatMessageHistory(
        session_id = thread_id,
        collection = "threads",
        client = client
    )
    chat_history.add_user_message(message)

def create_thread(thread_id):
    doc_ref = client.collection("threads").document(thread_id)
    doc_ref.set({
        "chatting_start_time": firestore.SERVER_TIMESTAMP
    })



